from typing import Dict, Optional

class SocraticDialogue:
    def __init__(self, llm_service, nlp_processor):
        self.llm_service = llm_service
        self.nlp_processor = nlp_processor
        self.socratic_prompt_template = """You are a modern Socrates, engaging in philosophical dialogue using the Socratic method. 
Your goal is to help the user think critically about their beliefs and assumptions through thoughtful questions.

Guidelines:
1. Ask probing questions that encourage deeper thinking
2. Challenge assumptions respectfully
3. Guide the user to discover insights on their own
4. Use examples and analogies when helpful
5. Be encouraging and supportive
6. Respond in a conversational, approachable manner

User's message: {message}

Analysis of user's input:
- Is a question: {is_question}
- Key concepts: {key_concepts}
- Word count: {word_count}
{category_info}

{context_info}

Please respond as Socrates would, focusing on helping the user explore their thoughts more deeply."""

    async def generate_response(
        self, 
        message: str, 
        processed_input: Dict,
        context: Optional[str] = None,
        category: Optional[str] = None,
        category_description: Optional[str] = None
    ) -> str:
        key_concepts = ', '.join(processed_input['filtered_tokens'][:10])
        
        context_info = ""
        if context:
            context_info = f"Previous context: {context}"
        
        category_info = ""
        if category and category_description:
            category_info = f"\n- Philosophical category: {category} - {category_description}"
        
        prompt = self.socratic_prompt_template.format(
            message=message,
            is_question=processed_input['is_question'],
            key_concepts=key_concepts,
            word_count=processed_input['word_count'],
            category_info=category_info,
            context_info=context_info
        )
        
        response = await self.llm_service.generate_response(prompt)
        return response