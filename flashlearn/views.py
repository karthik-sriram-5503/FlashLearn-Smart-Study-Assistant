from django.shortcuts import render

# Create your views here.
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.conf import settings
from .models import PDFDocument, Summary, Flashcard, ChatSession, ChatMessage
from .forms import PDFUploadForm, SummaryTopicForm, FlashcardGenerationForm, ChatForm
from .utils.pdf_processor import extract_main_headings, extract_topic_text, process_document_for_vector_store
from .utils.summarizer import summarize_text
from .utils.flashcard_generator import FlashcardGenerator
from .utils.embedding_store import EmbeddingStore
from .utils.chatbot import Chatbot
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse_lazy

def register_user(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {
        'form': form,
        'active_tab': 'register'
    })

def login_user(request):
    """Handle user login."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {
        'form': form,
        'active_tab': 'login'
    })

def logout_user(request):
    """Handle user logout."""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

def landing_page(request):
    """Landing page view."""
    # If user is already logged in, redirect to the application
    if request.user.is_authenticated:
        return redirect('home')
    
    return render(request, 'landing.html')

@login_required
def home(request):
    """Home page view."""
    form = PDFUploadForm()
    documents = PDFDocument.objects.all().order_by('-uploaded_at')
    
    # If user is not logged in, show landing page
    if not request.user.is_authenticated:
        return render(request, 'landing.html')
    
    return render(request, 'summarizer.html', {
        'form': form,
        'documents': documents,
        'active_tab': 'summarizer'
    })

@login_required
def upload_pdf(request):
    """Handle PDF upload."""
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user  # Assign document to the logged-in user
            document.save()
            messages.success(request, f"PDF '{document.title}' uploaded successfully.")
            return redirect('document_topics', document_id=document.id)
        else:
            messages.error(request, "Error uploading PDF. Please check the form.")
    return redirect('home')

@login_required
def document_topics(request, document_id):
    """Display document topics for selection."""
    document = get_object_or_404(PDFDocument, id=document_id)
    
    # Check if the document belongs to the logged-in user
    if document.user != request.user:
        messages.error(request, "You don't have permission to access this document.")
        return redirect('home')
    
    file_path = os.path.join(settings.MEDIA_ROOT, document.file.name)
    
    # Extract main headings
    headings = extract_main_headings(file_path)
    
    if not headings:
        messages.warning(request, "No main headings found in the PDF.")
        return redirect('home')
    
    # Prepare topics for form
    topics = [(f"{i}:{title}:{page}", f"{title} (Page {page})") for i, (title, page) in enumerate(headings)]
    
    form = SummaryTopicForm(topics=topics)
    
    return render(request, 'summarizer.html', {
        'document': document,
        'form': form,
        'active_tab': 'summarizer'
    })


@login_required
def generate_summary(request, document_id):
    """Generate summary for selected topic."""
    document = get_object_or_404(PDFDocument, id=document_id)
    
    if request.method == 'POST':
        topics = [(f"{i}:{title}:{page}", f"{title} (Page {page})") 
                 for i, (title, page) in enumerate(extract_main_headings(os.path.join(settings.MEDIA_ROOT, document.file.name)))]
        
        form = SummaryTopicForm(request.POST, topics=topics)
        
        if form.is_valid():
            # Parse the selected topic
            topic_data = form.cleaned_data['topic'].split(':')
            topic_index = int(topic_data[0])
            topic_title = topic_data[1]
            start_page = int(topic_data[2])
            
            # Extract and process text
            file_path = os.path.join(settings.MEDIA_ROOT, document.file.name)
            headings = extract_main_headings(file_path)
            
            end_page = headings[topic_index + 1][1] if topic_index + 1 < len(headings) else start_page + 10
            topic_text = extract_topic_text(file_path, start_page, end_page)
            
            # Generate summary
            summary_content = summarize_text(topic_text)
            
            # Save summary
            summary = Summary.objects.create(
                document=document,
                topic_title=topic_title,
                content=summary_content
            )
            
            messages.success(request, f"Summary generated for '{topic_title}'")
            return redirect('view_summary', summary_id=summary.id)
    
    return redirect('document_topics', document_id=document_id)

@login_required
def view_summary(request, summary_id):
    """View a generated summary."""
    summary = get_object_or_404(Summary, id=summary_id)
    
    return render(request, 'summarizer.html', {
        'document': summary.document,
        'summary': summary,
        'active_tab': 'summarizer'
    })

@login_required
def flashcards(request, summary_id):
    """Flashcards view for a summary."""
    summary = get_object_or_404(Summary, id=summary_id)
    flashcards = Flashcard.objects.filter(summary=summary).order_by('id')
    
    form = FlashcardGenerationForm()
    
    return render(request, 'flashcards.html', {
        'summary': summary,
        'flashcards': flashcards,
        'form': form,
        'active_tab': 'flashcards'
    })


@login_required
def generate_flashcards(request, summary_id):
    """Generate flashcards for a summary."""
    summary = get_object_or_404(Summary, id=summary_id)
    
    if request.method == 'POST':
        form = FlashcardGenerationForm(request.POST)
        
        if form.is_valid():
            num_cards = form.cleaned_data['num_cards']
            
            # Delete existing flashcards
            Flashcard.objects.filter(summary=summary).delete()
            
            # Generate new flashcards
            generator = FlashcardGenerator()
            flashcard_data = generator.generate_flashcards(summary.content, num_cards)
            
            # Save flashcards
            for question, answer in flashcard_data:
                Flashcard.objects.create(
                    summary=summary,
                    question=question,
                    answer=answer
                )
            
            messages.success(request, f"{len(flashcard_data)} flashcards generated successfully.")
    
    return redirect('flashcards', summary_id=summary.id)


@login_required
def chatbot(request, document_id):
    """Chatbot view for a document."""
    document = get_object_or_404(PDFDocument, id=document_id)
    
    # Get or create chat session
    chat_session, created = ChatSession.objects.get_or_create(document=document)
    
    # Get chat messages
    chat_messages = ChatMessage.objects.filter(session=chat_session).order_by('timestamp')
    
    form = ChatForm()
    
    # Check if vector store is created
    vector_store_exists = os.path.exists(os.path.join(settings.BASE_DIR, 'chroma_db'))
    
    return render(request, 'chatbot.html', {
        'document': document,
        'chat_session': chat_session,
        'chat_messages': chat_messages,
        'form': form,
        'vector_store_exists': vector_store_exists,
        'active_tab': 'chatbot'
    })

@require_POST
def create_knowledge_base(request, document_id):
    """Create knowledge base for document."""
    document = get_object_or_404(PDFDocument, id=document_id)
    
    try:
        # Process document for vector store
        file_path = os.path.join(settings.MEDIA_ROOT, document.file.name)
        splits = process_document_for_vector_store(file_path)
        
        # Create vector store
        embedding_store = EmbeddingStore()
        embedding_store.create_vector_store(splits)
        
        # Mark document as processed
        document.processed = True
        document.save()
        
        messages.success(request, "Knowledge base created successfully.")
        return JsonResponse({'status': 'success'})
    except Exception as e:
        messages.error(request, f"Error creating knowledge base: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_POST
def chat_message(request, document_id):
    """Handle chat message submission."""
    document = get_object_or_404(PDFDocument, id=document_id)
    
    # Get chat session
    chat_session, created = ChatSession.objects.get_or_create(document=document)
    
    form = ChatForm(request.POST)
    
    if form.is_valid():
        user_message = form.cleaned_data['message']
        
        # Save user message
        ChatMessage.objects.create(
            session=chat_session,
            role='user',
            content=user_message
        )
        
        # Get response from chatbot
        embedding_store = EmbeddingStore()
        retriever = embedding_store.get_retriever()
        
        if retriever:
            chatbot = Chatbot(retriever)
            response = chatbot.get_response(user_message)
            
            # Save assistant message
            ChatMessage.objects.create(
                session=chat_session,
                role='assistant',
                content=response
            )
        else:
            # Save error message
            ChatMessage.objects.create(
                session=chat_session,
                role='assistant',
                content="Please create a knowledge base first."
            )
    
    return redirect('chatbot', document_id=document.id)