from flask import Flask,jsonify, render_template

usha=Flask(__name__)                                            


@usha.route('/',methods=['GET'])
def root():
    namelist=['james','usha','jemu']
    usertype=['teacher','student','princi']
    return render_template('test.html',names=['james','usha','jemu'],usertypes=usertype)


if __name__ == '__main__':
    usha.run(debug=True)
