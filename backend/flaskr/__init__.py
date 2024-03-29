import os
from flask import Flask, request, abort, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# utility for paginating questions
def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'/': {'origins': '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    '''
    Sets access control.
    '''
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    '''
    Handles GET requests for getting all categories.
    '''

    # get all categories and add to dict
    categories = Category.query.all()
    categories_dict = {}
    for category in categories:
        categories_dict[category.id] = category.type

    # abort 404 if no categories found
    if (len(categories_dict) == 0):
        abort(404)

    # return data to view
    return jsonify({
        'success': True,
        'categories': categories_dict
    })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
      '''
      Handles GET requests for getting all questions.
      '''

      # get all questions and paginate
      selection = Question.query.order_by(Question.id).all()
      total_questions = len(selection)
      current_questions = paginate_questions(request, selection)

      # get all categories and add to dict
      categories = Category.query.all()
      categories_dict = {}
      for category in categories:
          categories_dict[category.id] = category.type

      # abort 404 if no questions
      if (len(current_questions) == 0):
          abort(404)

      # return data to view
      return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': total_questions,
          'categories': categories_dict
      })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route("/questions/<int:question_id>", methods=['DELETE'])
  def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except Exception as e:
            # abort(422)
            print("Error in delete question:" + str(e))

#   @app.route('/questions/<int:question_id>', methods=['DELETE'])
#   def delete_question(question_id):
#     '''
#     Handles DELETE requests for deleting a question by id.
#     '''
#     error_in_delete = False

#     try:
#       # get the question by id
#       question = Question.query.filter_by(question_id=id).one_or_none()

#       # abort 404 if no question found
#       if question is None:
#         abort(404)

#       # delete the question
#       question.delete()

#       # return success response
#       return jsonify({
#         'success': True,
#         'deleted': id
#       })
#     except Exception as e:
#         # abort if problem deleting question
#         # abort(422)
#         print("Error in delete question:" + str(e))
  

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def post_question():
    '''
    Handles POST requests for creating new questions and searching questions.
    '''
    # load the request body
    body = request.get_json()

    # if search term is present
    if (body.get('searchTerm')):
      search_term = body.get('searchTerm')

      # query the database using search term
      selection = Question.query.filter(
          Question.question.ilike(f'%{search_term}%')).all()

      # 404 if no results found
      if (len(selection) == 0):
          abort(404)

      # paginate the results
      paginated = paginate_questions(request, selection)

      # return results
      return jsonify({
          'success': True,
          'questions': paginated,
          'total_questions': len(Question.query.all())
      })
    # if no search term, create new question
    else:
        # load data from body
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_category = body.get('category')

        # ensure all fields have data
        if ((new_question is None) or (new_answer is None)
                or (new_difficulty is None) or (new_category is None)):
            abort(422)
            
        try:

            question = Question(
            question=new_question, 
            answer=new_answer,
            difficulty=new_difficulty, 
            category=new_category)

            question.insert()

            # get all questions and paginate
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            # flash('question was successfully created!')

            # return data to view
            return jsonify({
                'success': True,
                'created': question.id,
                'question_created': question.question,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })

        except Exception as e:
            print('Error message: ' + str(e))

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    '''
    Handles POST requests for creating new questions and searching questions.
    '''
    # load the request body
    body = request.get_json()

    # if search term is present
    if (body.get('searchTerm')):
      search_term = body.get('searchTerm')

      # query the database using search term
      selection = Question.query.filter(
          Question.question.ilike(f'%{search_term}%')).all()

      # 404 if no results found
      if (len(selection) == 0):
          abort(404)

      # paginate the results
      paginated = paginate_questions(request, selection)

      # return results
      return jsonify({
          'success': True,
          'questions': paginated,
          'total_questions': len(Question.query.all())
      })
    

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):
      '''
      Handles GET requests for getting questions based on category.
      '''

      # get the category by id
      category = Category.query.filter_by(id=id).one_or_none()

      # abort 400 for bad request if category isn't found
      if (category is None):
          abort(400)

      # get the matching questions
      selection = Question.query.filter_by(category=category.id).all()

      # paginate the selection
      paginated = paginate_questions(request, selection)

      # return the results
      return jsonify({
          'success': True,
          'questions': paginated,
          'total_questions': len(Question.query.all()),
          'current_category': category.type
      })


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_random_quiz_question():
      '''
      Handles POST requests for playing quiz.
      '''

      # load the request body
      body = request.get_json()

      # get the previous questions
      previous = body.get('previous_questions')

      # get the category
      category = body.get('quiz_category')

      # abort 400 if category or previous questions isn't found
      if ((category is None) or (previous is None)):
          abort(400)

      # load questions all questions if "ALL" is selected
      if (category['id'] == 0):
          questions = Question.query.all()
      # load questions for given category
      else:
          questions = Question.query.filter_by(category=category['id']).all()

      # get total number of questions
      total = len(questions)

      # picks a random question
      def get_random_question():
          return questions[random.randrange(0, len(questions), 1)]

      # checks to see if question has already been used
      def check_if_used(question):
          used = False
          for q in previous:
              if (q == question.id):
                  used = True

          return used

      # get random question
      question = get_random_question()

      # check if used, execute until unused question found
      while (check_if_used(question)):
          question = get_random_question()

          # if all questions have been tried, return without question
          # necessary if category has <5 questions
          if (len(previous) == total):
              return jsonify({
                  'success': True
              })

      # return the question
      return jsonify({
          'success': True,
          'question': question.format()
      })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  #___________ERROR HANDLER_______
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "bad request"
      }), 400

  
  return app

    