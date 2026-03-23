from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import Quiz, Question, Choice
from .utils import generate_quiz_from_topic
import threading

def home(request):
    if request.method == 'POST':
        topic = request.POST.get('topic')
        if topic:
            # Generate the quiz from AI
            try:
                quiz_data = generate_quiz_from_topic(topic)
                
                # Save to database
                quiz = Quiz.objects.create(title=quiz_data.get('title'), topic=topic)
                for q_data in quiz_data.get('questions', []):
                    question = Question.objects.create(quiz=quiz, text=q_data.get('text'))
                    for c_data in q_data.get('choices', []):
                        Choice.objects.create(
                            question=question,
                            text=c_data.get('text'),
                            is_correct=c_data.get('is_correct')
                        )
                return redirect('take_quiz', quiz_id=quiz.id)
            except Exception as e:
                return render(request, 'home.html', {'error': str(e)})

    return render(request, 'home.html')

def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        # Handle submission
        score = 0
        total = quiz.questions.count()
        results_data = []

        for question in quiz.questions.all():
            selected_choice_id = request.POST.get(f'question_{question.id}')
            correct_choice = question.choices.filter(is_correct=True).first()
            selected_choice = None
            is_correct = False

            if selected_choice_id:
                selected_choice = Choice.objects.filter(id=selected_choice_id).first()
                if selected_choice and selected_choice.is_correct:
                    score += 1
                    is_correct = True
                    
            results_data.append({
                'question_text': question.text,
                'selected_choice': selected_choice.text if selected_choice else "No answer",
                'correct_choice': correct_choice.text if correct_choice else "Unknown",
                'is_correct': is_correct
            })
        
        # Calculate percentage
        percentage = (score / total) * 100 if total > 0 else 0
        
        return render(request, 'quiz_results.html', {
            'quiz': quiz,
            'score': score,
            'total': total,
            'percentage': round(percentage, 2),
            'results_data': results_data
        })

    # Prepare data for frontend
    questions_data = []
    for question in quiz.questions.all():
        choices = []
        for choice in question.choices.all():
            choices.append({
                'id': choice.id,
                'text': choice.text,
            })
        questions_data.append({
            'id': question.id,
            'text': question.text,
            'choices': choices
        })

    return render(request, 'take_quiz.html', {
        'quiz': quiz,
        'questions': questions_data,
        'questions_count': len(questions_data)
    })
