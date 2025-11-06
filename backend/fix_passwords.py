"""Fix passwords for test accounts"""
from main import app, db, Student

with app.app_context():
    # Fix 24UCS153
    student1 = Student.query.filter_by(email='24ucs153kavin@kgkite.ac.in').first()
    if student1:
        test = student1.check_password('Kgkite@1234')
        if not test:
            student1.set_password('Kgkite@1234')
            print('[OK] Password reset for 24UCS153')
        else:
            print('[OK] Password OK for 24UCS153')
    
    # Fix 24UCS158
    student2 = Student.query.filter_by(email='24ucs158manisha@kgkite.ac.in').first()
    if student2:
        test = student2.check_password('Kgkite@1234')
        if not test:
            student2.set_password('Kgkite@1234')
            print('[OK] Password reset for 24UCS158')
        else:
            print('[OK] Password OK for 24UCS158')
    
    db.session.commit()
    print('\n[OK] All passwords verified and fixed!')
