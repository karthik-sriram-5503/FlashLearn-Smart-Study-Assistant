from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
import re
import ollama

class FlashcardGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.qg_model_name = "valhalla/t5-base-qg-hl"
        self.qa_model_name = "valhalla/t5-small-qa-qg-hl"
        
        # Load models and tokenizers
        self.qg_tokenizer = T5Tokenizer.from_pretrained(self.qg_model_name)
        self.qg_model = T5ForConditionalGeneration.from_pretrained(self.qg_model_name).to(self.device)
        
        self.qa_tokenizer = T5Tokenizer.from_pretrained(self.qa_model_name)
        self.qa_model = T5ForConditionalGeneration.from_pretrained(self.qa_model_name).to(self.device)

    def generate_flashcards(self, summary_text, num_cards=5):
        """Generate flashcards from a summary text."""
        sentences = re.split(r'(?<=[.!?])\s+', summary_text)
        paragraphs = []
        current_paragraph = ""

        for sentence in sentences:
            current_paragraph += sentence + " "
            if len(current_paragraph.split()) >= 30:
                paragraphs.append(current_paragraph.strip())
                current_paragraph = ""

        if current_paragraph.strip():
            paragraphs.append(current_paragraph.strip())

        flashcards = []
        cards_generated = 0

        for paragraph in paragraphs:
            if cards_generated >= num_cards:
                break

            qg_input = f"generate question: {paragraph}"
            qg_tokens = self.qg_tokenizer(qg_input, return_tensors="pt", max_length=512, truncation=True).to(self.device)
            qg_outputs = self.qg_model.generate(qg_tokens.input_ids, max_length=64, num_return_sequences=2, num_beams=4, early_stopping=True)

            for qg_output in qg_outputs:
                if cards_generated >= num_cards:
                    break

                question = self.qg_tokenizer.decode(qg_output, skip_special_tokens=True)
                if len(question) < 10 or not question.endswith('?'):
                    continue

                qa_input = f"question: {question} context: {paragraph}"
                qa_tokens = self.qa_tokenizer(qa_input, return_tensors="pt", max_length=512, truncation=True).to(self.device)
                qa_outputs = self.qa_model.generate(qa_tokens.input_ids, max_length=128, num_beams=4, early_stopping=True)
                answer = self.qa_tokenizer.decode(qa_outputs[0], skip_special_tokens=True)

                if 5 < len(answer) <= 200:
                    flashcards.append((question, answer))
                    cards_generated += 1

        return flashcards