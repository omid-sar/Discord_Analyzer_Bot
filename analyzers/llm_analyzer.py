import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from sqlalchemy.orm import Session
import tiktoken

from config.settings import settings
from models.database import Message, MessageAnalysis, PotentialCustomer, ChannelAnalysis

import logging
logger = logging.getLogger(__name__)

class LLMAnalyzer:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.encoding = tiktoken.encoding_for_model(settings.OPENAI_MODEL)
        
    async def analyze_channel(self, db: Session, channel_id: int) -> Dict[str, Any]:
        """Analyze all messages in a channel"""
        # Get messages from database
        messages = db.query(Message).filter_by(channel_id=channel_id).all()
        
        if not messages:
            return {"status": "no_messages", "potential_customers": []}
        
        logger.info(f"Analyzing {len(messages)} messages from channel {channel_id}")
        
        # Batch messages for analysis
        batches = self._create_message_batches(messages)
        
        all_analyses = []
        for i, batch in enumerate(batches):
            logger.info(f"Processing batch {i+1}/{len(batches)}")
            batch_analysis = await self._analyze_message_batch(db, batch)
            all_analyses.extend(batch_analysis)
            
            # Rate limiting
            await asyncio.sleep(settings.OPENAI_RATE_LIMIT_DELAY)
        
        # Aggregate results
        aggregated_results = await self._aggregate_analyses(db, all_analyses)
        
        # Save channel analysis
        self._save_channel_analysis(db, channel_id, aggregated_results)
        
        return aggregated_results
    
    def _create_message_batches(self, messages: List[Message]) -> List[List[Message]]:
        """Create batches of messages based on token count"""
        batches = []
        current_batch = []
        current_tokens = 0
        max_tokens = 3000  # Leave room for prompt
        
        for msg in messages:
            msg_tokens = len(self.encoding.encode(msg.content))
            
            if current_tokens + msg_tokens > max_tokens and current_batch:
                batches.append(current_batch)
                current_batch = []
                current_tokens = 0
            
            current_batch.append(msg)
            current_tokens += msg_tokens
        
        if current_batch:
            batches.append(current_batch)
            
        return batches
    
    async def _analyze_message_batch(self, db: Session, messages: List[Message]) -> List[Dict[str, Any]]:
        """Analyze a batch of messages using LLM"""
        # Prepare messages for analysis
        message_data = [
            {
                "id": msg.id,
                "author": msg.author_name,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat()
            }
            for msg in messages
        ]
        
        prompt = f"""Analyze the following Discord messages to identify potential customers for a startup.
For each message that shows customer intent, extract:
1. Intent score (0-1): How likely is this person to be a potential customer?
2. Intent type: What kind of intent are they showing? (seeking_solution, expressing_frustration, asking_recommendation, researching_options, etc.)
3. Pain points: What problems are they facing?
4. Interests: What are they looking for?
5. Keywords: Important keywords from their message

Focus on messages that contain:
- {', '.join(settings.CUSTOMER_KEYWORDS)}

Messages to analyze:
{json.dumps(message_data, indent=2)}

Return a JSON array with analysis for ONLY messages showing customer intent:
[
  {{
    "message_id": 123,
    "author": "username",
    "intent_score": 0.85,
    "intent_type": "seeking_solution",
    "pain_points": ["specific problem"],
    "interests": ["what they want"],
    "keywords": ["important", "words"],
    "explanation": "Why this is a potential customer"
  }}
]

Only include messages with intent_score > 0.3"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying potential customers from conversations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={ "type": "json_object" }
            )
            
            result = json.loads(response.choices[0].message.content)
            analyses = result if isinstance(result, list) else result.get('analyses', [])
            
            # Save individual message analyses
            for analysis in analyses:
                msg = next((m for m in messages if m.id == analysis['message_id']), None)
                if msg:
                    self._save_message_analysis(db, msg, analysis)
            
            return analyses
            
        except Exception as e:
            logger.error(f"Error analyzing message batch: {e}")
            return []
    
    def _save_message_analysis(self, db: Session, message: Message, analysis: Dict[str, Any]):
        """Save message analysis to database"""
        try:
            # Check if analysis already exists
            existing = db.query(MessageAnalysis).filter_by(message_id=message.id).first()
            
            if not existing:
                msg_analysis = MessageAnalysis(
                    message_id=message.id,
                    intent_score=analysis.get('intent_score', 0),
                    intent_type=analysis.get('intent_type', ''),
                    sentiment='neutral',  # Can be enhanced later
                    keywords=analysis.get('keywords', []),
                    insights=analysis.get('explanation', '')
                )
                db.add(msg_analysis)
                db.commit()
                
        except Exception as e:
            logger.error(f"Error saving message analysis: {e}")
            db.rollback()
    
    async def _aggregate_analyses(self, db: Session, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate individual analyses into customer profiles"""
        # Group by author
        author_data = {}
        for analysis in analyses:
            author = analysis['author']
            if author not in author_data:
                author_data[author] = {
                    'analyses': [],
                    'pain_points': set(),
                    'interests': set(),
                    'total_score': 0,
                    'message_count': 0
                }
            
            author_data[author]['analyses'].append(analysis)
            author_data[author]['pain_points'].update(analysis.get('pain_points', []))
            author_data[author]['interests'].update(analysis.get('interests', []))
            author_data[author]['total_score'] += analysis.get('intent_score', 0)
            author_data[author]['message_count'] += 1
        
        # Create potential customer profiles
        potential_customers = []
        
        for author, data in author_data.items():
            avg_score = data['total_score'] / data['message_count']
            
            if avg_score > 0.5:  # Threshold for potential customer
                # Get or create potential customer
                self._update_potential_customer(db, author, data, avg_score)
                
                potential_customers.append({
                    'username': author,
                    'score': avg_score,
                    'pain_points': list(data['pain_points']),
                    'interests': list(data['interests']),
                    'message_count': data['message_count'],
                    'engagement_level': self._calculate_engagement_level(avg_score, data['message_count'])
                })
        
        # Sort by score
        potential_customers.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'status': 'success',
            'total_messages_analyzed': len(analyses),
            'potential_customers': potential_customers,
            'summary': await self._generate_summary(potential_customers)
        }
    
    def _update_potential_customer(self, db: Session, username: str, data: Dict[str, Any], score: float):
        """Update or create potential customer record"""
        try:
            # For now, use username as ID (in real implementation, use Discord user ID)
            customer = db.query(PotentialCustomer).filter_by(username=username).first()
            
            if not customer:
                customer = PotentialCustomer(
                    discord_user_id=username,  # Should be actual Discord ID
                    username=username,
                    score=score,
                    pain_points=list(data['pain_points']),
                    interests=list(data['interests']),
                    engagement_level=self._calculate_engagement_level(score, data['message_count']),
                    first_seen=datetime.utcnow(),
                    last_seen=datetime.utcnow(),
                    message_count=data['message_count']
                )
                db.add(customer)
            else:
                # Update existing customer
                customer.score = (customer.score + score) / 2  # Average scores
                customer.pain_points = list(set(customer.pain_points + list(data['pain_points'])))
                customer.interests = list(set(customer.interests + list(data['interests'])))
                customer.last_seen = datetime.utcnow()
                customer.message_count += data['message_count']
                customer.engagement_level = self._calculate_engagement_level(customer.score, customer.message_count)
                customer.updated_at = datetime.utcnow()
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error updating potential customer: {e}")
            db.rollback()
    
    def _calculate_engagement_level(self, score: float, message_count: int) -> str:
        """Calculate engagement level based on score and activity"""
        if score > 0.8 and message_count > 5:
            return 'high'
        elif score > 0.6 or message_count > 3:
            return 'medium'
        else:
            return 'low'
    
    async def _generate_summary(self, potential_customers: List[Dict[str, Any]]) -> str:
        """Generate a summary of the analysis"""
        if not potential_customers:
            return "No potential customers identified in this analysis."
        
        top_pain_points = {}
        for customer in potential_customers:
            for pain_point in customer['pain_points']:
                top_pain_points[pain_point] = top_pain_points.get(pain_point, 0) + 1
        
        sorted_pain_points = sorted(top_pain_points.items(), key=lambda x: x[1], reverse=True)
        
        summary = f"Identified {len(potential_customers)} potential customers. "
        summary += f"Top pain points: {', '.join([pp[0] for pp in sorted_pain_points[:3]])}. "
        summary += f"High engagement users: {sum(1 for c in potential_customers if c['engagement_level'] == 'high')}"
        
        return summary
    
    def _save_channel_analysis(self, db: Session, channel_id: int, results: Dict[str, Any]):
        """Save channel analysis to database"""
        try:
            analysis = ChannelAnalysis(
                channel_id=channel_id,
                analysis_type='customer_intent',
                summary=results.get('summary', ''),
                insights={
                    'potential_customers_count': len(results.get('potential_customers', [])),
                    'messages_analyzed': results.get('total_messages_analyzed', 0),
                    'top_customers': [
                        {
                            'username': c['username'],
                            'score': c['score']
                        }
                        for c in results.get('potential_customers', [])[:5]
                    ]
                }
            )
            db.add(analysis)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error saving channel analysis: {e}")
            db.rollback()
    
    async def generate_customer_report(self, db: Session) -> Dict[str, Any]:
        """Generate a comprehensive customer report"""
        customers = db.query(PotentialCustomer).all()
        
        if not customers:
            return {
                'total_customers': 0,
                'high_priority_count': 0,
                'total_messages': 0,
                'top_pain_points': []
            }
        
        # Aggregate pain points
        all_pain_points = {}
        for customer in customers:
            for pain_point in customer.pain_points:
                all_pain_points[pain_point] = all_pain_points.get(pain_point, 0) + 1
        
        sorted_pain_points = sorted(all_pain_points.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_customers': len(customers),
            'high_priority_count': sum(1 for c in customers if c.engagement_level == 'high'),
            'total_messages': sum(c.message_count for c in customers),
            'top_pain_points': [
                {'pain_point': pp[0], 'count': pp[1]}
                for pp in sorted_pain_points[:10]
            ],
            'customers': [
                {
                    'username': c.username,
                    'score': c.score,
                    'engagement_level': c.engagement_level,
                    'pain_points': c.pain_points[:5],
                    'interests': c.interests[:5]
                }
                for c in sorted(customers, key=lambda x: x.score, reverse=True)[:20]
            ]
        } 