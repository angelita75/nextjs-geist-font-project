from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from database import db
from diary import diary_bp
from models import DiaryEntry, Comment, Like

@diary_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_diary():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        safety_tips = request.form.get('safety_tips')
        diary = DiaryEntry(user_id=current_user.id, title=title, body=body, safety_tips=safety_tips)
        db.session.add(diary)
        db.session.commit()
        flash('Diary entry created.')
        return redirect(url_for('diary.view_diaries'))
    return render_template('diary/create_edit.html', action='Create')

@diary_bp.route('/edit/<int:diary_id>', methods=['GET', 'POST'])
@login_required
def edit_diary(diary_id):
    diary = DiaryEntry.query.get_or_404(diary_id)
    if diary.user_id != current_user.id:
        flash('You do not have permission to edit this diary.')
        return redirect(url_for('diary.view_diaries'))
    if request.method == 'POST':
        diary.title = request.form['title']
        diary.body = request.form['body']
        diary.safety_tips = request.form.get('safety_tips')
        db.session.commit()
        flash('Diary entry updated.')
        return redirect(url_for('diary.view_diaries'))
    return render_template('diary/create_edit.html', diary=diary, action='Edit')

@diary_bp.route('/delete/<int:diary_id>', methods=['POST'])
@login_required
def delete_diary(diary_id):
    diary = DiaryEntry.query.get_or_404(diary_id)
    if diary.user_id != current_user.id:
        flash('You do not have permission to delete this diary.')
        return redirect(url_for('diary.view_diaries'))
    db.session.delete(diary)
    db.session.commit()
    flash('Diary entry deleted.')
    return redirect(url_for('diary.view_diaries'))

@diary_bp.route('/all')
def view_diaries():
    diaries = DiaryEntry.query.order_by(DiaryEntry.timestamp.desc()).all()
    return render_template('diary/all_diaries.html', diaries=diaries)

@diary_bp.route('/comment', methods=['POST'])
@login_required
def add_comment():
    diary_id = request.form['diary_id']
    body = request.form['body']
    comment = Comment(diary_id=diary_id, user_id=current_user.id, body=body)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'status': 'success', 'comment': body})

@diary_bp.route('/like', methods=['POST'])
@login_required
def like_diary():
    diary_id = request.form['diary_id']
    like = Like.query.filter_by(diary_id=diary_id, user_id=current_user.id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        liked = False
    else:
        new_like = Like(diary_id=diary_id, user_id=current_user.id)
        db.session.add(new_like)
        db.session.commit()
        liked = True
    like_count = Like.query.filter_by(diary_id=diary_id).count()
    return jsonify({'liked': liked, 'like_count': like_count})
