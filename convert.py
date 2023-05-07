# A program that allows you to write ti-basic programs in your own editor, and convert them to .8xp files with macros for the weird syntaces.
# Substitutes the hard characters, see help below.
#V2.1.0


#Future features:
#-Better Menu macros, allowing custom label and routines

import subprocess

def main():
    f=""
    while True:
        f = input("enter fp (.8xpe, no extension in fp), h for help   ")
        f8 = f + ".8xpe"
        if f == "h":
            print("Write a program in ti-basic and save it to a \".8xpe\" file!")
            print("Except, you don't have to do it in the editor!")
            print("Use improved shorthands for the clunky language!")
            print("Bind variable names at the top of your program: &bee&B    and then call with underscores bee_*2->bee_")
            print("Similar with labels: at the top of your program: |home|H   and no underscore     Goto home")
            print("Make comments with /* */ or // : all text in between pairs will be ignored")
            print("Bind all at the top of the program, variables before labels")
            print("Use your own editor like VSCODE to have personal version control for your program.")
            print("Substitutions:")
            print("List operator character: instead of the little L, l_")
            print("For the default lists, use L_")
            print("Sto operator character: instead of the arrow, ->")
            print("Theta character: _theta_")
            print("Replace math comparison operators with traditional code ones: <, >, <=, >=, =, !=")
            print("Newlines delimit statements as normal")
            print("If need to continue a line, use a semicolon (sorry!)") 
            print("Spaces after commas are ignored")
            print("Replace all \"End\" with right curly bracket and Then with left bracket, but don't put a left bracket on a For loop.")
            print("Cosmetic brackets for for loops or Lbls can be done with {.  and }.   but indentation is recommended instead ")
            print("Y1 etc vars: Y_n for n the number")
            print("All other syntax must align with ti-basic, including extraneous spaces after lone keywords.")

            #Order of parsing evaluation:
            # Comments
            # Brackets & Gotos
            # Other substitutions
            # Whitespace destruction
            # Bindings
        else:
            break
    convert(f)



def convert(f):
    #Start Conversion
    original_program = ""

    #Open .8xpe
    with open(f + ".8xpe",mode='r',encoding="utf-8") as file:
        original_program = file.read()

    #Substitutions, will add to then substitute
    replacement_list = [\
    ("{.",""),\
    ("}.",""),\
    ("{", "\nThen"),\
    ("}", "\nEnd"),\
    (";\n",""),\
    ("->", "→"),\
    ("_theta_", "θ"),\
    ("Y_0", "Y₀"),\
    ("Y_1", "Y₁"),\
    ("Y_2", "Y₂"),\
    ("Y_3", "Y₃"),\
    ("Y_4", "Y₄"),\
    ("Y_5", "Y₅"),\
    ("Y_6", "Y₆"),\
    ("Y_7", "Y₇"),\
    ("Y_8", "Y₈"),\
    ("Y_9", "Y₉"),\
    ("L_1", "L₁"),\
    ("L_2", "L₂"),\
    ("L_3", "L₃"),\
    ("L_4", "L₄"),\
    ("L_5", "L₅"),\
    ("L_6", "L₆"),\
    ("l_", "⌊"),\
    (">=", "≥"),\
    ("<=", "≤"),\
    ("!=", "≠"),\
    ]


    #Substitutions that repeat until no more are found
    exhaustive_replacement_list = [\
    ("\n ", "\n"),\
    (" \n", "\n"),\
    (", ", ","),\
    (" ,", ","),\
    ("-> ", "->"),\
    (" ->", "->"),\
    ]

    #Comments /* */
    commented = original_program.split("/*")
    lefts = len(commented) - 1
    rights = 0
    accum = commented[0]
    for i in range(1, len(commented)):
        if commented[i].count("*/") > 1:
            print("Syntax Error: Extra */ in comment")
            exit()
        rights += commented[i].count("*/")
        accum += commented[i].split("*/")[1]
    if lefts != rights:
        print("Syntax Error: Unbalanced Commments")
        exit() 

    #Comments //
    original_program = accum
    commented = original_program.split("//")
    accum = commented[0]
    for i in range(1, len(commented)):
        accum += '\n'+commented[i].partition('\n')[2]

    original_program = accum


    #Bind variables
    split_by_amper = original_program.split("&")
    section_count = len(split_by_amper)

    if section_count > 1: #If there are binds

        if section_count % 2 == 0:
            print("Syntax Error: Unclosed & expression")
            exit()

        if split_by_amper[0].strip() != "":
            print("Syntax Error: Extra code before & binds")

        for i in range(1,len(split_by_amper)):
            n = split_by_amper[i].strip()

            if i % 2 == 1: #Bind varible name
                replacing = n;
                if not n.isalnum():
                    print("Syntax Error: Variable bind name illegal")
                    exit()

            else: #Bind variable letter
                if len(n) != 1 and i != section_count-1:
                    print(n)
                    print("Syntax Error: Extra code in between binds")
                    exit()
                if not n[0].isalpha() or not n[0].isupper():
                    print("Syntax Error: & bind not followed by legal variable")
                    exit()

                replacement_list.append((replacing+"_",n[0]))
    original_program = split_by_amper[-1][1:].strip()


    #Bind labels
    split_by_vert = original_program.split("|")
    section_count = len(split_by_vert)
    if section_count > 1: #If there are binds

        if section_count % 2 == 0:
            print("Syntax Error: Unclosed | expression")
            exit()

        if split_by_vert[0].strip() != "":
            print("Syntax Error: Extra code before | binds")

        for i in range(1,len(split_by_vert)):
            n = split_by_vert[i].strip()

            if i % 2 == 1: #Bind name
                replacing = n;
                if not n.isalnum():
                    print("Syntax Error: Variable bind name not alphanumeric")
                    exit()

            else: #Bind label letter pair
                if len(n) > 2 and i != len(split_by_vert)-1:
                    print(n)
                    print("Syntax Error: Extra code in between binds")
                    exit()

                invalid_first_letter = not n[0].isalpha() or not n[0].isupper()
                invalid_second_letter_exist = not (n[1].isalnum() or n[1].strip() == "")
                invalid_second_letter_case = (n[1].isalpha() and not n[1].isupper())

                if invalid_first_letter or invalid_second_letter_exist or invalid_second_letter_case:
                    print("Syntax Error: | bind not followed by legal label")
                    exit()

                replacement_list.append(("Goto "+replacing,"Goto "+n[0:2]))
                replacement_list.append(("Lbl "+replacing,"Lbl "+n[0:2]))
                replacement_list.append((","+replacing,","+n[0:2]))
    original_program = split_by_vert[-1][2:].strip()
        
    #Replace
    for i in replacement_list:
        original_program = original_program.replace(i[0],i[1])

    for i in exhaustive_replacement_list:
        copy = ""
        while copy != original_program:
            copy = original_program
            original_program = original_program.replace(i[0],i[1])

    #Write
    with open(f+".8xpt.temp",mode='w', encoding = 'utf-8') as file:
        file.write(original_program)

    #Create new file for copying (or outputting if using converter script)
    with open(f+".8xp",mode='w') as file:
        pass #create new file
 
if __name__ != "__main__":
    print("Run convert.py as the main file")
    exit()
else:
    main()

# Not functional, doensn't ironically convert special characters
# subprocess.run(["8xp_original.exe", f+".8xpt.temp", f+".8xp"])

#/pick up later
#use calc.exe in folder to convert, subprocess.run
#programs in progress: ptaylor, aamath, ppoly