from flask import Blueprint, render_template, url_for, request, session, flash, redirect
from flask_login import logout_user, current_user, login_required
from datetime import datetime
from .models import *
from .wtform_fields import *

bp = Blueprint('main', __name__)

@bp.route('/<username>/home')
@login_required
#user specific
def home(username):
    user=User.query.filter_by(username=username).first()
    categories = Category.query.filter(Category.userid==user.id).all()
    dailyrecords = DailyRecord.query.filter(DailyRecord.user_id==current_user.id).order_by(DailyRecord.datetime).limit(10).all()
    dailyexercises = DailyExercise.query.all()
    return render_template('home.html', user=user, categories = categories, dailyrecords = dailyrecords, dailyexercises = dailyexercises)

#see the menus for a specific part 
@bp.route('/<username>/menulog/<int:categoryid>/')
#user specific
def menulog(categoryid, username):
    user=User.query.filter_by(username=username).first()
    categories = Category.query.filter(Category.id==categoryid)
    exercises = Exercise.query.filter(Exercise.category_id == categoryid, Exercise.user_id == user.id)
    return render_template('menulog.html', exercises = exercises, categories = categories)

#see all the menus 
@bp.route('/<username>/allmenus')
def allmenulog(username):
    user=User.query.filter_by(username=username).first()
    categories = Category.query.filter(Category.userid==current_user.id).all()
    exercises = Exercise.query.filter(Exercise.user_id == user.id).all()

    return render_template('allmenulog.html', exercises = exercises, categories = categories)

@bp.route('/<username>/alldailyrecords')
def alldailyrecord(username):
    dailyrecords = DailyRecord.query.filter(DailyRecord.user_id==current_user.id).order_by(DailyRecord.datetime).all()
    dailyexercises = DailyExercise.query.all()

    return render_template('alldailyrecord.html', dailyrecords = dailyrecords, dailyexercises = dailyexercises)

###### Addition #########

#add new category (training part)
@bp.route('/categoryreg', methods=['GET', 'POST'])
@login_required
def categoryreg():
    category_form = CategoryRegForm()

    if category_form.validate_on_submit():
        name = category_form.category_name.data
        userid = current_user.id

        category = Category(name=name, userid=userid)
        db.session.add(category)
        db.session.commit()

        flash('Your category successfully added!', 'success')

        return redirect(url_for('main.categoryreg'))

    return render_template('categoryreg.html', form = category_form) 

#Add new menu to the database
@bp.route('/menureg', methods=['GET', 'POST'])
@login_required
def menureg():
    exercise_form = ExerciseRegForm()

    if exercise_form.validate_on_submit():
        name = exercise_form.exercise_name.data
        part = exercise_form.exercise_part.data.id #get id from category!!!!
        weight = exercise_form.exercise_weight.data
        rep = exercise_form.exercise_rep.data
        sets= exercise_form.exercise_sets.data
        user_id = current_user.id

        exercise = Exercise(name=name, category_id = part, weight = weight, rep = rep, sets = sets, user_id = user_id)
        db.session.add(exercise)
        db.session.commit()

        flash('Your exercise successfully added!','success')

        return redirect(url_for('main.menureg'))

    return render_template('menureg.html', form = exercise_form)

#Adding daily record
@bp.route('/dailyrecord', methods=['GET', 'POST'])
@login_required
def dailyrecord():
    daily_record_form = DailyRecordForm()

    if daily_record_form.validate_on_submit():
        dt = datetime.now()
        category = daily_record_form.today_part.data.name
        user_id = current_user.id

        dailyrecord = DailyRecord(datetime = dt, category = category, user_id = user_id)
        db.session.add(dailyrecord)
        db.session.commit()

        return redirect(url_for('main.dailyexercises'))

    return render_template('dailyrecord.html', form = daily_record_form)

#Register exercises in daily record
@bp.route('/dailyexercises', methods=['GET', 'POST'])
@login_required
def dailyexercises():
    daily_exercise_form = DailyExerciseForm()
    userid=current_user.id

    if daily_exercise_form.validate_on_submit():
        
        dailyrecordid = DailyRecord.query.filter(DailyRecord.user_id==userid).order_by(DailyRecord.datetime.desc()).first().id
        exercise = daily_exercise_form.today_exercise.data.name
        weight = daily_exercise_form.today_weight.data
        rep = daily_exercise_form.today_rep.data
        sets = daily_exercise_form.today_sets.data

        dailyexercise = DailyExercise(dailyrecord_id = dailyrecordid, exercise = exercise, weight = weight, rep = rep, sets = sets)
        db.session.add(dailyexercise)
        db.session.commit()

        flash('Successfully added', 'success')

        return redirect(url_for('main.dailyexercises'))

    return render_template('dailyexercise.html', form = daily_exercise_form)

####Deletion#####

#Delete category
@bp.route('/deletecategory/<int:id>', methods=['POST'])
@login_required
def deletecategory(id):

    #delete category itself
    category = Category.query.filter_by(id=id).first()
    db.session.delete(category)

    #delete all the exercises in the category
    exercises = Exercise.query.filter(Exercise.category_id==id).all()
    for exercise in exercises:
        db.session.delete(exercise)

    db.session.commit()

    flash('the exercise successfully deleted', 'success')

    return redirect(url_for('main.allmenulog', username=current_user.username))

#Delete menu
@bp.route('/deletemenu/<int:id>', methods=['POST'])
@login_required
def deletemenu(id):
    menu = Exercise.query.filter_by(id=id).first()
    name = Exercise.query.filter_by(id=id).first().name
    dailyexercise = DailyExercise.query.filter(DailyExercise.exercise==name).all()

    #delete from menu
    db.session.delete(menu)

    #delete from daily records
    for exercise in dailyexercise:
        db.session.delete(exercise)

    db.session.commit()

    flash('the exercise successfully deleted', 'success')

    return redirect(url_for('main.allmenulog', username=current_user.username))

#Delete daily exercise from daily record
@bp.route('/deletedailyexercise/<int:id>', methods=['POST'])
@login_required
def deletedailyexercise(id):
    dailyexercise = DailyExercise.query.filter_by(id=id).first()

    db.session.delete(dailyexercise)
    db.session.commit()

    flash('the exercise record is successfully deleted','success')

    return redirect(url_for('main.alldailyrecord', username=current_user.username))

#Delete daily record itself
@bp.route('/deletedailyrecord/<int:id>', methods=['POST'])
@login_required
def deletedailyrecord(id):
    dailyrecord = DailyRecord.query.filter_by(id=id).first()
    dailyexercises = DailyExercise.query.filter(DailyExercise.dailyrecord_id==id).all()

    db.session.delete(dailyrecord)

    if dailyexercises is not None:
        for dailyexercise in dailyexercises:
            db.session.delete(dailyexercise)

    db.session.commit()

    flash('the exercise record is successfully deleted','success')

    return redirect(url_for('main.alldailyrecord', username=current_user.username))

#logout
@bp.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('index'))