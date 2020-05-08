import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS ,cross_origin
import logging

import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app) 
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"*": {"origins": "*"}})
  # cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger(__name__)
  QUASTIONS_PER_CATEGURY = 10
  def paginate_qustion(request, selection):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * QUASTIONS_PER_CATEGURY
    end = start + QUASTIONS_PER_CATEGURY

    qustions = [question.format() for question in selection]
    current_qustions = qustions[start:end]

    return current_qustions
  
  # '''
  # @TODO: 
  # Create an endpoint to handle GET requests 
  # for all available categories.
  # '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
      categories = Category.query.all()
      category_formatted = {category.id: category.type for category in categories}

      result = {
            "success": True,
            "categories":category_formatted
        }
      return jsonify(result)



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
  @app.route('/questions', methods=['GET'])
  def get_questions():
    # question = list(map(Question.format, Question.query.all()))

    # result={
    #   "success":True,
    #    "questions": question
    # }
    # questions = list(map(Question.format, Question.query.all()))
    # questions = Question.query.order_by(Question.id).all()
    questions = Question.query.all()
    total_questions = len(questions)
    categories = Category.query.all()
    category_formatted = {category.id: category.type for category in categories}
    current_qustions = paginate_qustion(request,questions)

    if len(current_qustions) == 0:
      abort(404)

    result={
     'success': True,
     'questions':current_qustions,
     'total_questions': total_questions,
     'categories':category_formatted,
     "current_category": None

    }
    return jsonify(result)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>',methods=['GET','DELETE'])
  def delete_question(question_id):
    question = Question.query.filter(Question.id == question_id).one_or_none()

    if question == None:
      
        abort(404)
    else:
      question.delete()

    return jsonify({
      'success':True

    })
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
  def new_questions():
    new_question =  request.json.get('question')
    new_answer = request.json.get('answer')
    new_difficulty = request.json.get('difficulty')
    new_category = request.json.get('category')



    try:
       question = Question(question=new_question,answer=new_answer ,category=new_category ,difficulty=new_difficulty)
       question.insert()
     
       logger.info("info message ffffffffffffffffffffffsfsf %s" % question.format() )

       questions_query = Question.query.all()
       return jsonify({
      'success' : True,
       "question": question.format(),
      #  "current_category": 1
       })
    except:
      abort(422)

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
  def search_questions():
    body = request.get_json()
    app.logger.info('reach serach!!!!!!!!!!!!! %s', body)
    search = body.get('search', None) 
    logger.info("info message ffffffffffffffffffffffsfsf %s" % search )
    if search is None or search == '':
        abort(400)

    try:
        result = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
        qustion = [q.format() for q in result]
        # x = Question.query.all()
        total_questions = len(qustion) 
        return jsonify({
      'success' : True,
      'questions':qustion,
      'total_questions': total_questions,
      'current_category': [(question['category'])
                         for question in qustion]
      })
    except BaseException:
      abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def category_of_question(category_id):
    category_id = str(category_id)
    question = Question.query.filter_by(category=category_id).all()
    current_qustions = paginate_qustion(request,question)


    return jsonify({
      'success' : True,
      'questions':current_qustions,
      'total_questions':len(question),
      # 'current_category':[(question['category'])
      #                    for question in question]
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
  def play_quiz():
    data = request.get_json()
    previous_questions = data.get('previous_questions', None)
    app.logger.info('pr!!!!!!!!!!!!!%s', previous_questions)
    quiz_category = data.get('quiz_category', None)
    # app.logger.info('quiz_category!!!!!!!!!!!!!%s', quiz_category)
    category_id = int(quiz_category['id'])
    app.logger.info('category_id!!!!!!!!!!!!!%s', category_id)

    if category_id != 0:
       questions = Question.query.filter_by(category=str(category_id)).all()
    else:
      questions = Question.query.all()

    available_questions = []
    for question in questions:
      if question.format() not in previous_questions:
        available_questions.append(question.format())

    if len(available_questions)>0:
        choice = available_questions[random.randint( 0, len(available_questions)-1)]
        previous_questions.append(choice)
        return jsonify({
                    "success": True,
                    "question": choice,
                    "previous_questions": previous_questions,
                    'quiz_category': quiz_category
                })
    else:
                return jsonify({
                    "success": True,
                    'question': 'This is the End of the Questions',
                    "previous_questions": previous_questions,
                    'quiz_category': quiz_category
                })
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "Page Not Found"
      }), 404
  @app.errorhandler(422)
  def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        }), 422
  @app.errorhandler(400)
  def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400
  @app.errorhandler(500)
  def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Server Internal Error"
        }), 500
  return app

    
