STYLE = """
QMainWindow{
    background:#202124;
}

QWidget{
    background:#202124;
    color:white;
    font-size:14px;
}

QGroupBox{
    border:2px solid #3a3a3a;
    border-radius:10px;
    margin-top:10px;
    font-weight:bold;
    padding-top:12px;
}

QLineEdit,
QComboBox,
QTextEdit{

    background:#2b2b2b;
    color:white;

    border:1px solid #555;

    border-radius:8px;

    padding:8px;
}

QPushButton{

    background:#ff0000;

    color:white;

    border:none;

    border-radius:8px;

    padding:10px;

    font-weight:bold;

}

QPushButton:hover{

    background:#d50000;

}

QPushButton:pressed{

    background:#990000;

}

QProgressBar{

    border:none;

    border-radius:8px;

    background:#3a3a3a;

    text-align:center;

}

QProgressBar::chunk{

    background:#ff0000;

    border-radius:8px;

}
"""