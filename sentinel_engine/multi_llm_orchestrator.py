"""
Sentinel Engine Phase 2 - Multi-LLM Orchestrator
Zero-cost revenue engine using free API tiers
"""
import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import tiktoken

logger = logging.getLogger(__name__)

class MultiLLMOrchestrator:
    """
    Multi-LLM orchestration system for Phase 2 revenue generation
    Routes tasks to optimal providers based on task type and cost
    """
    
    def __init__(self):
        self.providers = {
            'groq': {
                'strength': 'speed',
                'cost_per_token': 0.0,  # Free tier
                'models': ['llama3-8b-8192', 'llama3-70b-8192'],
                'temperature_range': (0.0, 1.0)
            },
            'openai': {
                'strength': 'general',
                'cost_per_token': 0.0015,  # GPT-3.5-turbo
                'models': ['gpt-3.5-turbo', 'gpt-4o-mini'],
                'temperature_range': (0.0, 2.0)
            },
            'anthropic': {
                'strength': 'reasoning',
                'cost_per_token': 0.003,  # Claude Haiku
                'models': ['claude-3-haiku-20240307'],
                'temperature_range': (0.0, 1.0)
            },
            'google': {
                'strength': 'analysis',
                'cost_per_token': 0.0,  # Free tier
                'models': ['gemini-1.5-flash'],
                'temperature_range': (0.0, 2.0)
            }
        }
        
        # Task type routing
        self.task_routing = {
            'technical': {'provider': 'anthropic', 'temperature': 0.1},
            'creative': {'provider': 'openai', 'temperature': 0.7},
            'coding': {'provider': 'groq', 'temperature': 0.0},
            'analysis': {'provider': 'google', 'temperature': 0.3},
            'speed': {'provider': 'groq', 'temperature': 0.2},
            'general': {'provider': 'openai', 'temperature': 0.5}
        }
        
        self.usage_stats = {
            'total_requests': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'provider_usage': {}
        }
    
    async def route_task(self, prompt: str, task_type: str = 'general', 
                        use_consensus: bool = False, budget_limit: float = 1.0) -> Dict[str, Any]:
        """
        Route task to optimal LLM provider
        """
        try:
            if use_consensus:
                return await self._consensus_processing(prompt, task_type, budget_limit)
            else:
                return await self._single_provider_processing(prompt, task_type, budget_limit)
                
        except Exception as e:
            logger.error(f"LLM routing error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': None,
                'response': None
            }
    
    async def _single_provider_processing(self, prompt: str, task_type: str, 
                                        budget_limit: float) -> Dict[str, Any]:
        """Process with single optimal provider"""
        
        # Get routing config
        routing = self.task_routing.get(task_type, self.task_routing['general'])
        provider_name = routing['provider']
        temperature = routing['temperature']
        
        # Check if we have API key for this provider
        if not self._has_api_key(provider_name):
            # Fallback to free providers
            free_providers = [p for p in self.providers.keys() 
                            if self.providers[p]['cost_per_token'] == 0.0 
                            and self._has_api_key(p)]
            
            if not free_providers:
                return {
                    'success': False,
                    'error': 'No API keys configured for any provider',
                    'provider': None,
                    'response': None
                }
            
            provider_name = free_providers[0]
        
        # Process with selected provider
        result = await self._call_provider(provider_name, prompt, temperature, budget_limit)
        
        # Update usage stats
        self._update_usage_stats(provider_name, result)
        
        return result
    
    async def _consensus_processing(self, prompt: str, task_type: str, 
                                  budget_limit: float) -> Dict[str, Any]:
        """Process with multiple providers and consensus"""
        
        # Select 2-3 providers for consensus
        available_providers = [p for p in self.providers.keys() if self._has_api_key(p)]
        
        if len(available_providers) < 2:
            return await self._single_provider_processing(prompt, task_type, budget_limit)
        
        # Select top providers for this task type
        consensus_providers = available_providers[:3]  # Use first 3 available
        
        # Run parallel processing
        tasks = []
        for provider in consensus_providers:
            task = self._call_provider(provider, prompt, 0.3, budget_limit / len(consensus_providers))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process consensus results
        successful_results = [r for r in results if isinstance(r, dict) and r.get('success')]
        
        if not successful_results:
            return {
                'success': False,
                'error': 'All consensus providers failed',
                'provider': 'consensus',
                'response': None
            }
        
        # Simple consensus: return best result based on response length and success
        best_result = max(successful_results, 
                         key=lambda x: len(x.get('response', '')) if x.get('response') else 0)
        
        # Update stats for all providers
        for result in successful_results:
            if result.get('provider'):
                self._update_usage_stats(result['provider'], result)
        
        best_result['consensus_count'] = len(successful_results)
        best_result['provider'] = 'consensus'
        
        return best_result
    
    async def _call_provider(self, provider: str, prompt: str, 
                           temperature: float, budget_limit: float) -> Dict[str, Any]:
        """Call specific LLM provider"""
        
        try:
            if provider == 'groq':
                return await self._call_groq(prompt, temperature)
            elif provider == 'openai':
                return await self._call_openai(prompt, temperature, budget_limit)
            elif provider == 'anthropic':
                return await self._call_anthropic(prompt, temperature, budget_limit)
            elif provider == 'google':
                return await self._call_google(prompt, temperature)
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': provider,
                'response': None,
                'tokens': 0,
                'cost': 0.0
            }
    
    async def _call_groq(self, prompt: str, temperature: float) -> Dict[str, Any]:
        """Call Groq API (free tier)"""
        try:
            import groq
            
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key or api_key == 'your_groq_key_here':
                raise ValueError("Groq API key not configured")
            
            client = groq.Groq(api_key=api_key)
            
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else self._estimate_tokens(prompt + content)
            
            return {
                'success': True,
                'provider': 'groq',
                'response': content,
                'tokens': tokens_used,
                'cost': 0.0,  # Free tier
                'model': 'llama3-8b-8192'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Groq error: {str(e)}",
                'provider': 'groq',
                'response': None,
                'tokens': 0,
                'cost': 0.0
            }
    
    async def _call_openai(self, prompt: str, temperature: float, budget_limit: float) -> Dict[str, Any]:
        """Call OpenAI API"""
        try:
            import openai
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key or api_key == 'your_openai_key_here':
                raise ValueError("OpenAI API key not configured")
            
            client = openai.OpenAI(api_key=api_key)
            
            # Estimate cost before making call
            estimated_tokens = self._estimate_tokens(prompt) + 500  # Estimate response
            estimated_cost = estimated_tokens * 0.0015 / 1000  # GPT-3.5-turbo pricing
            
            if estimated_cost > budget_limit:
                raise ValueError(f"Estimated cost ${estimated_cost:.4f} exceeds budget ${budget_limit:.4f}")
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            actual_cost = tokens_used * 0.0015 / 1000
            
            return {
                'success': True,
                'provider': 'openai',
                'response': content,
                'tokens': tokens_used,
                'cost': actual_cost,
                'model': 'gpt-3.5-turbo'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"OpenAI error: {str(e)}",
                'provider': 'openai',
                'response': None,
                'tokens': 0,
                'cost': 0.0
            }
    
    async def _call_anthropic(self, prompt: str, temperature: float, budget_limit: float) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        try:
            import anthropic
            
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key or api_key == 'your_anthropic_key_here':
                raise ValueError("Anthropic API key not configured")
            
            client = anthropic.Anthropic(api_key=api_key)
            
            # Estimate cost
            estimated_tokens = self._estimate_tokens(prompt) + 500
            estimated_cost = estimated_tokens * 0.003 / 1000  # Claude Haiku pricing
            
            if estimated_cost > budget_limit:
                raise ValueError(f"Estimated cost ${estimated_cost:.4f} exceeds budget ${budget_limit:.4f}")
            
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            actual_cost = tokens_used * 0.003 / 1000
            
            return {
                'success': True,
                'provider': 'anthropic',
                'response': content,
                'tokens': tokens_used,
                'cost': actual_cost,
                'model': 'claude-3-haiku-20240307'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Anthropic error: {str(e)}",
                'provider': 'anthropic',
                'response': None,
                'tokens': 0,
                'cost': 0.0
            }
    
    async def _call_google(self, prompt: str, temperature: float) -> Dict[str, Any]:
        """Call Google Gemini API (free tier)"""
        try:
            import google.generativeai as genai
            
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key or api_key == 'your_google_key_here':
                raise ValueError("Google API key not configured")
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=1000
                )
            )
            
            content = response.text
            tokens_used = self._estimate_tokens(prompt + content)
            
            return {
                'success': True,
                'provider': 'google',
                'response': content,
                'tokens': tokens_used,
                'cost': 0.0,  # Free tier
                'model': 'gemini-1.5-flash'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Google error: {str(e)}",
                'provider': 'google',
                'response': None,
                'tokens': 0,
                'cost': 0.0
            }
    
    def _has_api_key(self, provider: str) -> bool:
        """Check if API key is configured for provider"""
        key_map = {
            'groq': 'GROQ_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'google': 'GOOGLE_API_KEY'
        }
        
        key_name = key_map.get(provider)
        if not key_name:
            return False
        
        key_value = os.getenv(key_name)
        return key_value and key_value != f'your_{provider}_key_here'
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        try:
            enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
        except:
            # Fallback: roughly 4 characters per token
            return len(text) // 4
    
    def _update_usage_stats(self, provider: str, result: Dict[str, Any]):
        """Update usage statistics"""
        if not result.get('success'):
            return
        
        tokens = result.get('tokens', 0)
        cost = result.get('cost', 0.0)
        
        self.usage_stats['total_requests'] += 1
        self.usage_stats['total_tokens'] += tokens
        self.usage_stats['total_cost'] += cost
        
        if provider not in self.usage_stats['provider_usage']:
            self.usage_stats['provider_usage'][provider] = {
                'requests': 0,
                'tokens': 0,
                'cost': 0.0
            }
        
        self.usage_stats['provider_usage'][provider]['requests'] += 1
        self.usage_stats['provider_usage'][provider]['tokens'] += tokens
        self.usage_stats['provider_usage'][provider]['cost'] += cost
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage summary for reporting"""
        return {
            'summary': self.usage_stats,
            'cost_savings': self._calculate_cost_savings(),
            'provider_performance': self._get_provider_performance(),
            'recommendations': self._get_recommendations()
        }
    
    def _calculate_cost_savings(self) -> Dict[str, Any]:
        """Calculate cost savings vs single provider"""
        total_tokens = self.usage_stats['total_tokens']
        actual_cost = self.usage_stats['total_cost']
        
        # Calculate what it would cost with single expensive provider
        openai_cost = total_tokens * 0.0015 / 1000
        anthropic_cost = total_tokens * 0.003 / 1000
        
        savings_vs_openai = max(0, openai_cost - actual_cost)
        savings_vs_anthropic = max(0, anthropic_cost - actual_cost)
        
        return {
            'actual_cost': actual_cost,
            'openai_cost': openai_cost,
            'anthropic_cost': anthropic_cost,
            'savings_vs_openai': savings_vs_openai,
            'savings_vs_anthropic': savings_vs_anthropic,
            'savings_percentage': ((max(openai_cost, anthropic_cost) - actual_cost) / max(openai_cost, anthropic_cost, 0.001)) * 100
        }
    
    def _get_provider_performance(self) -> Dict[str, Any]:
        """Analyze provider performance"""
        performance = {}
        
        for provider, stats in self.usage_stats['provider_usage'].items():
            if stats['requests'] > 0:
                performance[provider] = {
                    'requests': stats['requests'],
                    'avg_cost_per_request': stats['cost'] / stats['requests'] if stats['requests'] > 0 else 0,
                    'tokens_per_request': stats['tokens'] / stats['requests'] if stats['requests'] > 0 else 0,
                    'total_cost': stats['cost']
                }
        
        return performance
    
    def _get_recommendations(self) -> List[str]:
        """Get optimization recommendations"""
        recommendations = []
        
        # Check if using free tiers effectively
        free_usage = sum(stats['requests'] for provider, stats in self.usage_stats['provider_usage'].items() 
                        if self.providers.get(provider, {}).get('cost_per_token', 0) == 0)
        total_requests = self.usage_stats['total_requests']
        
        if total_requests > 0:
            free_percentage = (free_usage / total_requests) * 100
            
            if free_percentage < 50:
                recommendations.append("Consider using more free-tier providers (Groq, Google) to reduce costs")
            
            if self.usage_stats['total_cost'] > 10:
                recommendations.append("High costs detected - consider implementing more aggressive free-tier routing")
            
            if len(self.usage_stats['provider_usage']) < 2:
                recommendations.append("Consider enabling multiple providers for redundancy and cost optimization")
        
        return recommendations

# Global instance
multi_llm = MultiLLMOrchestrator()
