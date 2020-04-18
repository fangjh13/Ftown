for post_id in [22, 10, 21]:
    p = Post.query.filter_by(id=post_id).first()
    for c in p.comments.all():
        author = c.author
        db.session.delete(c)
        db.session.delete(author)
    db.session.commit()