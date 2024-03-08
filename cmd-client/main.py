#Finex
#Version 1
try:
  import cutie, copy, calendar, random, locale, prettytable, os
  import sqlite3
  from sys import platform
  from datetime import *
except:
  print("Preparing Finex")
  os.system("pip install cutie")
  os.system("pip install prettytable")

locale.setlocale(locale.LC_ALL, 'en_IN.utf8')
orgData = ""

def cls():

    if platform == "linux" or platform == "linux2" or platform=='darwin':
        os.system("clear")
    else:
        os.system("cls")


def format_string(val):
    return locale.format_string("%d", val, grouping=True)

def fa_management(msg):
    while True:
        mycursor.execute(f"SELECT account_name from fixed_assets where orgID={orgData[0][0]}")
        myresult=mycursor.fetchall()
        if myresult==[] or msg=="IGNORE":
            mycursor.execute(f"SELECT account_name from coa where orgID={orgData[0][0]} and category in ('A', 'L', 'C') and fa_id is null")
            myresult=mycursor.fetchall()
            accounts = []
            if myresult==[]:
                cls()
                print("You have not added any ledger accounts for financing the Asset. Add an account and return back here")
                return "TOBEADDED"
            else:
                for account in myresult:
                    accounts.append(account[0])
                if msg!="IGNORE":
                    ch = cutie.prompt_yes_or_no("You have not added any fixed assets for management. Add an asset?")
                else:
                    ch = True
                if ch==True:
                    cls()
                    account_name = input("Enter the name of the Asset")
                    mycursor.execute(f"SELECT count(account_name) from coa where account_name like '%{account_name}%' and account_name not like '%Gain on Sale of {account_name}%' and account_name not like '%Loss on Sale of {account_name}%'")
                    myresult=mycursor.fetchall()
                    num = myresult[0][0]
                    if num==0:
                        account_name+=f" ({str(1)})"
                    else:
                        num+=1
                        new_num = str(num)
                        account_name+=f" ({new_num})"
                    lifespan = int(cutie.get_number("How much is the estimated life span of the asset", 1))
                    ch_1 = cutie.prompt_yes_or_no("Is the asset subjected to higher repairs and maintenance when it nears it's lifespan?")
                    ch_2 = cutie.prompt_yes_or_no("Is the asset exposed to higher risks of obsolescense?")
                    if ch_1==True and ch_2==True:
                        print("We determined that the Written Down Value Method is best for the Asset\n-> The Written Down Value Method (WDV) charges higher depreciation in an asset's early life, when it's work efficiency is at maximum.\n-> It is used by Income Tax Authorities\n-> Depreciation goes on reducing year to year\n.-> The amount of depreciation and the repairs amount to the P&L account will be uniform year-to-year.\n\n")
                        ch = cutie.prompt_yes_or_no("Agree with WDV or use SLM?")
                        if ch==True:
                            method = "WDV"
                        else:
                            method = "SLM"
                    else:
                        print("We determined that the Straight Line Method is best for the Asset\n-> The Straight Line Method (SLM) charges equal amount of depreciation to an asset \n-> It is suitable for assets who does not have much repair charges and for those assets whose loss due to obsolescense is low\n\n")
                        ch = cutie.prompt_yes_or_no("Agree with SLM or use WDV?")
                        if ch==True:
                            method = "SLM"
                        else:
                            method = "WDV"
                    date_ = input("Enter the date of the transaction in YYYY-MM-DD format, including the dashes")
                    print("How did you finance the Asset")
                    credit_acc = accounts[cutie.select(accounts)]
                    narration = input("Enter a narration for the transaction (OPTIONAL)")
                    amount = float(input("Enter the purchase price of the asset"))
                    ch = int(input("Enter the estimated scrap value of the asset"))
                    per = cutie.get_number("Enter the rate of percentage for charging depreciation. Just enter the number")
                    faId = random.randint(10000,99999)
                    mycursor.execute(f"INSERT INTO fixed_assets VALUES({orgData[0][0]}, '{account_name}', {lifespan}, '{method}', {amount}, {per/100}, '{date_}', {faId})")
                    mycursor.execute(f"INSERT INTO coa VALUES({orgData[0][0]}, '{account_name}', 'A', {faId})")
                    mycursor.execute(f"SELECT max(trx_id) from journal where orgID={orgData[0][0]}")
                    trx_id = mycursor.fetchall()[0][0]
                    if trx_id==None:
                        trx_id=1
                    else:
                        trx_id+=1
                    mycursor.execute(f"INSERT INTO journal VALUES({orgData[0][0]}, '{date_}', '{account_name}', '{credit_acc}', '{narration}', {amount}, {trx_id})")
                    con.commit()
                    print("Asset account created successfully")
                    msg = ""
                else:
                    cls()
        else:
            print(f"You have {len(myresult)} assets")
            mycursor.execute(f"SELECT account_name from fixed_assets where orgID={orgData[0][0]}")
            myresult=mycursor.fetchall()
            print(f"Manage assets")
            assets = []
            for asset in myresult:
                assets.append(asset[0])
            assets.append('Back')
            assets.append("Add a new asset")
            asset = assets[cutie.select(assets)]
            if asset!="Back" and asset!="Add a new asset":
                cls()
                mycursor.execute(f"SELECT account_name, ls, method, pp, dep, dp from fixed_assets where orgID={orgData[0][0]} and account_name='{asset}'")
                asset_details=mycursor.fetchall()
                print("Name of the Asset:", asset_details[0][0])
                print("Expected Life Span of the Asset:", asset_details[0][1], "years")
                print("Method of charging Depreciation:", asset_details[0][2])
                print("Purchase price of the Asset:", asset_details[0][3])
                ori_sum_debit=ori_sum_credit=0
                t = prettytable.PrettyTable()
                t.field_names=["Date", "Particulars", "Dr. Amount", "Cr. Amount"]
                ori_sum_debit=ori_sum_credit=0
                start_of_month = datetime.now().replace(year=datetime.now().year - 1, month=4, day=1)
                end_of_month = datetime.now()
                accounts = asset_details[0][0]
                t.title = f"{accounts} Account from {start_of_month.date()} to {end_of_month.date()}"
                mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date<'{start_of_month}') order by trx_date")
                myresult = mycursor.fetchall()
                if myresult!=[]:
                    for trx in myresult:
                        if trx[1]==accounts:
                            ori_sum_debit+=trx[4]
                        else:
                            ori_sum_credit+=trx[4]
                mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date between '{start_of_month}' and '{end_of_month}') order by trx_date")
                myresult = mycursor.fetchall()
                if myresult!=[]:
                    sum_debit, sum_credit = 0, 0
                    t.add_row(["", "Balance b/d", format_string(ori_sum_debit-ori_sum_credit), ""], divider=True)
                    sum_debit+=ori_sum_debit-ori_sum_credit
                    for trx in myresult:
                        if trx[1]==accounts:
                            t.add_row([trx[0], trx[2], format_string(int(trx[4])), ""])
                            sum_debit+=trx[4]
                            pass
                        else:
                            t.add_row([trx[0], trx[1], "", format_string(int(trx[4]))])
                            sum_credit+=trx[4]
                            pass
                    if sum_debit>sum_credit:
                        t.add_row(["", "Balance c/d", "", format_string(sum_debit-sum_credit)], divider=True)
                        t.add_row(["", "Total", format_string(sum_debit), format_string(sum_debit)])

                    else:
                        t.add_row(["", "", "", ""], divider=True)
                        t.add_row(["", "", format_string(sum_debit), format_string(sum_credit)])
                else:
                    t.add_row(["", "Balance c/d", "", format_string(ori_sum_debit-ori_sum_credit)], divider=True)
                print(t)
                today = datetime.now()
                if asset_details[0][2]=="SLM":
                    start_of_month = (datetime.now().replace(year=datetime.now().year - 1, month=4, day=1)).date()
                    end_of_month = (today.replace(day=31, month=3)).date()
                    mycursor.execute(f"SELECT '{asset_details[0][-1]}' between '{start_of_month}' and '{end_of_month}'")
                    myresult = mycursor.fetchall()
                    if myresult[0][0]==1:
                        dp = (asset_details[0][-1]).month
                        delta = (datetime.now().date()-(asset_details[0][-1])).days
                        today = (datetime.now()).month
                        if dp==today:
                            months = 1
                        else:
                            months = (today-dp)+1
                        dep = int(asset_details[0][3]*(asset_details[0][4]/100)*months/12)
                        dep_ = int(asset_details[0][3]*(asset_details[0][4]/100)*delta/365)
                    else:
                        dep = int(asset_details[0][3]*(asset_details[0][4]/100))
                        dep_ = int(asset_details[0][3]*(asset_details[0][4]/100)*delta/365)

                else:
                    start_of_month = (datetime.now().replace(year=datetime.now().year - 1, month=4, day=1)).date()
                    end_of_month = (today.replace(day=31, month=3)).date()
                    mycursor.execute(f"SELECT '{asset_details[0][-1]}' between '{start_of_month}' and '{end_of_month}'")
                    myresult = mycursor.fetchall()
                    if myresult[0][0]==1:
                        dp = (asset_details[0][-1]).month
                        delta = (datetime.now().date()-(asset_details[0][-1])).days
                        today = (datetime.now()).month
                        if dp==today:
                            months = 1
                        else:
                            months = (today-dp)+1
                        dep = int(asset_details[0][3]*(asset_details[0][4]/100)*months/12)
                        dep_ = int(asset_details[0][3]*(asset_details[0][4]/100)*delta/365)
                    else:
                        dep = int(balance*(asset_details[0][4]/100))
                        dep_ = int(balance*(asset_details[0][4]/100)*delta/365)
                print("Amount of depreciation to be charged on 31st March:", dep)
                today = datetime.now()
                if today.date() == 31 and today.month==3:
                    try:
                        mycursor.execute(f"INSERT INTO coa VALUES({orgData[0][0]}, 'Depreciation', 'IE', NULL)")
                    except:
                        pass
                    narration = f"Being depreciation for {asset_details[0][0]} for the accounting year {today.year-1}-{today.year}"
                    amount = dep
                    mycursor.execute(f"SELECT max(trx_id) from journal where orgID={orgData[0][0]}")
                    trx_id = mycursor.fetchall()[0][0]
                    if trx_id==None:
                        trx_id=1
                    else:
                        trx_id+=1
                    mycursor.execute(f"INSERT INTO journal VALUES({orgData[0][0]}, '{today.date()}', 'Depreciation', '{asset_details[0][0]}', '{narration}', {amount}, {trx_id})")
                    con.commit()
                else:
                    print("Finex will charge depreciation to asset on 31st March")
                if sum_debit-sum_credit>0:
                    print(f"Manage Asset: {asset_details[0][0]}")
                    options = ["Dispose Asset", "Back"]
                    option = options[cutie.select(options)]
                    if option=="Dispose Asset":
                        print("Are you:-")
                        options = ["Disposing the asset fully", "Disposing a part of the asset"]
                        option=options[cutie.select(options)]
                        if option=="Disposing the asset fully":
                            balance = sum_debit-sum_credit
                            sp = cutie.get_number('Enter the sale price of the asset')
                            mycursor.execute(f"SELECT account_name from coa where orgID={orgData[0][0]} and (category='A' and fa_id is null)")
                            myresult=mycursor.fetchall()
                            accounts = []
                            for account in myresult:
                                accounts.append(account[0])
                            print("How did you sell the Asset")
                            debit_acc = accounts[cutie.select(accounts)]
                            print("Depreciation to be charged today:", dep_)
                            balance-=dep_
                            balance-=sp
                            pl = balance
                            if pl>0:
                                try:
                                    mycursor.execute(f"INSERT INTO coa VALUES({orgData[0][0]}, 'Loss on Sale of {asset_details[0][0]}', 'IE', NULL)")
                                    con.commit()
                                except:
                                    pass
                                print("Loss of ₹",pl)
                            elif pl<0:
                                try:
                                    mycursor.execute(f"INSERT INTO coa VALUES({orgData[0][0]}, 'Gain on Sale of {asset_details[0][0]}', 'II', NULL)")
                                    con.commit()
                                except:
                                    pass
                                print("Gain of ₹", pl)
                            else:
                                print("No Loss No Profit")
                            confirm = cutie.prompt_yes_or_no("Are you sure to confirm the disposal of the Asset?")
                            if confirm==True:
                                try:
                                    mycursor.execute(f"INSERT INTO coa VALUES({orgData[0][0]}, 'Depreciation', 'IE', NULL)")
                                    con.commit()
                                except:
                                    pass
                                narration = f"Being depreciation for {asset_details[0][0]} charged"
                                amount = dep_
                                mycursor.execute(f"SELECT max(trx_id) from journal where orgID={orgData[0][0]}")
                                trx_id = mycursor.fetchall()[0][0]
                                if trx_id==None:
                                    trx_id=1
                                else:
                                    trx_id+=1
                                mycursor.execute(f"INSERT INTO journal VALUES({orgData[0][0]}, '{today.date()}', 'Depreciation', '{asset_details[0][0]}', '{narration}', {amount}, {trx_id})")
                                trx_id+=1
                                if pl>0:
                                    mycursor.execute(f"INSERT INTO journal VALUES({orgData[0][0]}, '{today.date()}', 'Loss on Sale of {asset_details[0][0]}', '{asset_details[0][0]}', 'Being {asset_details[0][0]} disposed completely at a loss', {pl}, {trx_id})")
                                elif pl<0:
                                    mycursor.execute(f"INSERT INTO journal VALUES({orgData[0][0]}, '{today.date()}', '{asset_details[0][0]}', 'Gain on Sale of {asset_details[0][0]}', 'Being {asset_details[0][0]} disposed completely at a gain', {-pl}, {trx_id})")
                                trx_id+=1
                                mycursor.execute(f"INSERT INTO journal VALUES({orgData[0][0]}, '{today.date()}', '{debit_acc}', '{asset_details[0][0]}', 'Being {asset_details[0][0]} disposed', {sp}, {trx_id})")
                                mycursor.execute(f"DELETE FROM fixed_assets WHERE account_name='{asset_details[0][0]} and orgID={orgData[0][0]}'")
                                mycursor.execute(f"UPDATE coa SET fa_id=0 WHERE account_name='{asset_details[0][0]}'")
                                con.commit()
                        else:
                            if asset_details[0][2]=="SLM":
                                balance = sum_debit-sum_credit
                                cp = cutie.get_number("Enter the cost price of the part of the asset you are disposing")
                                cost = copy.copy(cp)
                                if cp>balance:
                                    print("Enter valid cost price of the part of the asset you are disposing")
                                else:
                                    sp = cutie.get_number('Enter the sale price of the asset')
                                    today = datetime.now()
                                    diff = (today-asset_details[0][-1]).days
                                    dep_=cp*asset_details[0][4]*diff/365
                                    print(f"Depreciation to be charged today = {int(dep_)}")
                                    cp-=dep_
                                    cp-=sp
                                    pl = cp
                                    if pl>0:
                                        try:
                                            mycursor.execute(f"INSERT INTO coa VALUES({orgData[0][0]}, Loss on Sale of Part of '{asset_details[0][0]}', 'IE')")
                                        except:
                                            pass
                                        print("Loss of ₹",pl)
                                    else:
                                        try:
                                            mycursor.execute(f"INSERT INTO coa VALUES({orgData[0][0]}, Gain on Sale of Part of '{asset_details[0][0]}', 'II')")
                                        except:
                                            pass
                                        print("Gain of ₹", int(-pl))
                                    confirm = cutie.prompt_yes_or_no("Are you sure to confirm the disposal of the Asset?")
                                    if confirm==True:
                                        try:
                                            mycursor.execute(f"INSERT INTO coa VALUES({orgData[0][0]}, 'Depreciation', 'IE', NULL)")
                                            con.commit()
                                        except:
                                            pass
                                        narration = f"Being depreciation for {asset_details[0][0]} charged"
                                        amount = dep_
                                        mycursor.execute(f"SELECT max(trx_id) from journal where orgID={orgData[0][0]}")
                                        trx_id = mycursor.fetchall()[0][0]
                                        if trx_id==None:
                                            trx_id=1
                                        else:
                                            trx_id+=1
                                        mycursor.execute(f"INSERT INTO journal VALUES({orgData[0][0]}, '{today.date()}', 'Depreciation', '{asset_details[0][0]}', '{narration}', {amount}, {trx_id})")
                                        trx_id+=1
                                        print(pl)
                                        if pl>0:
                                            mycursor.execute(f"INSERT INTO journal VALUES({orgData[0][0]}, '{today.date()}', 'Loss on Sale of Part of {asset_details[0][0]}', '{asset_details[0][0]}', 'Being {asset_details[0][0]} disposed partially at a loss', {pl}, {trx_id})")
                                        elif pl<0:
                                            mycursor.execute(f"INSERT INTO journal VALUES({orgData[0][0]}, '{today.date()}', '{asset_details[0][0]}', 'Gain on Sale of {asset_details[0][0]}', 'Being {asset_details[0][0]} disposed partially at a gain', {int(-pl)}, {trx_id})")
                                        trx_id+=1
                                        mycursor.execute(f"INSERT INTO journal VALUES({orgData[0][0]}, '{today.date()}', '{debit_acc}', '{asset_details[0][0]}', 'Being {asset_details[0][0]} disposed partially', {sp}, {trx_id})")
                                        mycursor.execute(f"UPDATE fixed_assets SET pp={asset_details[0][3]-{cost}} where account_name = {asset_details[0][0]} and orgID={orgData[0][0]}")
                                        con.commit()
                            else:
                                print("Currently, partial disposal of assets following WDV is not supported")
            elif asset=="Back":
                cls()
                break
            else:
                fa_management("IGNORE")

                break


con = sqlite3.connect('finex.db')
mycursor = con.cursor()
mycursor.execute("CREATE TABLE IF NOT EXISTS orgs (orgID int primary key, orgName varchar(30), orgAddress varchar(500), orgEmail varchar(100), orgPassword varchar(500))")
mycursor.execute("CREATE TABLE IF NOT EXISTS fixed_assets (orgID int, account_name varchar(50), ls int, method char(3), pp float, dep float, dp date, fa_id int primary key)")
mycursor.execute("CREATE TABLE IF NOT EXISTS coa (orgID int, account_name varchar(50) NOT NULL, category char(2) NOT NULL, fa_id int references fixed_assets(fa_id), PRIMARY KEY (orgID,account_name))")
mycursor.execute("CREATE TABLE IF NOT EXISTS journal (orgID int, trx_date date, debit_account varchar(50), credit_account varchar(50), narration varchar(5000), amount float, trx_id int)")

print("Welcome to Finex\nDeveloped by ASA Finserve\n")

options = ["Login", "Signup", "About", "Exit"]
while True:
    option = options[cutie.select(options)]
    if option=="Signup":
        cls()
        orgID = random.randint(10000,99999)
        mycursor.execute(f"SELECT orgID from orgs where orgID={orgID}")
        myresult = mycursor.fetchall()
        if myresult!=[]:
            orgID = random.randint(10000,99999)
        orgName = input("Enter your organisation's name")
        orgAddress = input("Enter your organisation's registered address \n(This will be used in the header of various reports generated by Finex)\n")
        orgEmail = input("Enter your organisation's email ID (This is used for auto sending of reports)")
        orgPassword = cutie.secure_input("Enter a secure password for this organisation")
        length = len(orgPassword)
        mycursor.execute(f"INSERT INTO orgs VALUES({orgID}, '{orgName}', '{orgAddress}', '{orgEmail}', '{orgPassword}')")
        con.commit()
        cls()
        print(f"Success! Your organisation {orgName} has been added successfully. Please remember your Organisation ID and Password carefully\nOrganisation ID : {orgID}\nPassword : ", end="")
        print("*"*length)
        continue
    elif option=="Login":
        cls()
        orgID = int(input("Enter your Organisation ID"))
        mycursor.execute(f"SELECT * from orgs where orgID={orgID}")
        orgData = mycursor.fetchall()
        if orgData==[]:
            print("Invalid Organisation ID")
            continue
        else:
            password = cutie.secure_input("Enter your password")
            if (orgData[0][4])==(password):
                break
            else:
                print("Incorrect password")
                continue

    elif option=="About":
        cls()
        print("Finex\nAn accounting software created by ASA Finserve to help businesses of any size manage their day-to-day transactions easily.\n")
        continue
    else:
        exit()
cls()
msg = ""
while True:
    print(f"Welcome back, {orgData[0][1]}")
    today = datetime.now()
    mycursor.execute(f"SELECT account_name from coa where orgID={orgData[0][0]}")
    myresult=mycursor.fetchall()
    if myresult!=[] and today.date==31 and today.month==3:
        choice = cutie.prompt_yes_or_no("Today is 31st March. Close all books of accounts?")
        if choice==True:
            print("Will perform closing entries soon")
        else:
            print("Ok")

    options = ["Journal", "Ledger & Accounts", "Financial Reports", "Fixed Assets Management", "Settings", "Exit"]
    option = options[cutie.select(options)]
    if option=="Ledger & Accounts":
        cls()
        mycursor.execute(f"SELECT account_name from coa where orgID={orgData[0][0]}")
        myresult=mycursor.fetchall()
        if myresult==[]:
            print("You have not created any accounts. Create an account to access Journal and Ledger")
            try:
                account_name = input("Enter the name of the account. Press CTRL+C to quit")
                list_of_assets = ["Machinery", "Land", "Building", "Land & Building", "Plant", "Plant & Machinery", "Furniture", "Vehicles"]
                if account_name in list_of_assets:
                    print("You are trying to add a Fixed Asset. We recommend that you add it through the Fixed Assets Management, so that your asset can automatically be depreciated at the year-end. You can also easily have features for disposal of the asset")
                    ch = cutie.prompt_yes_or_no("Are you sure you wish to continue? ")
                    if ch==True:
                        result = fa_management("")
                        if result=="TOBEADDED":
                            continue
                    else:
                        pass
            except:
                continue
            options = ["Asset", "Liability", "Income", "Capital", "Expense"]
            classification = options[cutie.select(options)]
            if classification=="Asset":
                classification="A"
            elif classification=="Liability":
                classification="L"
            elif classification=="Income":
                options = ["Direct Income", "Indirect Income"]
                option = options[cutie.select(options)]
                if option=="Direct Income":
                    classification="DI"
                else:
                    classification="II"
            elif classification=="Capital":
                classification="C"
            else:
                options = ["Direct Expense", "Indirect Expense"]
                option = options[cutie.select(options)]
                if option=="Direct Expense":
                    classification="DE"
                else:
                    classification="IE"
            mycursor.execute(f"INSERT INTO coa VALUES({orgData[0][0]}, '{account_name}', '{classification}', NULL)")
            con.commit()
            cls()
            print("Account created successfully")
        else:
            print("Select an account")
            account_list = []
            for account in myresult:
                account_list.append(account[0])
            account_list.append("Create a new account")
            accounts = account_list[cutie.select(account_list)]
            if accounts=="Create a new account":
                cls()
                try:
                    account_name = input("Enter the name of the account. Press CTRL+C to quit")
                    list_of_assets = ["Machinery", "Land", "Building", "Land & Building", "Plant", "Plant & Machinery", "Furniture", "Vehicles"]
                    if account_name in list_of_assets:
                        print("You are trying to add a Fixed Asset. We recommend that you add it through the Fixed Assets Management, so that your asset can automatically be depreciated at the year-end. You can also easily have features for disposal of the asset")
                        ch = cutie.prompt_yes_or_no("Are you sure you wish to continue? ")
                        if ch==True:
                            fa_management("")
                            continue
                        else:
                            pass

                except KeyboardInterrupt:
                    exit()
                options = ["Asset", "Liability", "Income", "Capital", "Expense"]
                classification = options[cutie.select(options)]
                if classification=="Asset":
                    classification="A"
                elif classification=="Liability":
                    classification="L"
                elif classification=="Income":
                    options = ["Direct Income", "Indirect Income"]
                    option = options[cutie.select(options)]
                    if option=="Direct Income":
                        classification="DI"
                    else:
                        classification="II"
                elif classification=="Capital":
                    classification="C"
                else:
                    options = ["Direct Expense", "Indirect Expense"]
                    option = options[cutie.select(options)]
                    if option=="Direct Expense":
                        classification="DE"
                    else:
                        classification="IE"
                mycursor.execute(f"INSERT INTO coa VALUES({orgData[0][0]}, '{account_name}', '{classification}', NULL)")
                con.commit()
                cls()
                print("Account created successfully")
            else:
                cls()
                t = prettytable.PrettyTable()
                t.field_names=["Date", "Particulars", "Dr. Amount", "Cr. Amount"]
                mycursor.execute(f"select distinct MonthNAME(trx_date) as month, YEAR(trx_date) as Year, month(trx_date) from journal where debit_account='{accounts}' or credit_account='{accounts}'")
                myresult=mycursor.fetchall()
                print(f"Select Time Period for viewing transactions of {accounts} account. You can select multiple months by pressing SPACE BAR")
                option = ["Today", "Yesterday", "This Week", "This Month", "This Quarter", "Last Quarter", "Last Month", "Calender Year till date", "Accounting Year till date", "Custom Range"]
                options = option[cutie.select(option)]
                if options=="Today":
                    ori_sum_debit=ori_sum_credit=0
                    todayDate = date.today()
                    t.title=f"{accounts} Account from {todayDate} to {todayDate}"
                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date<'{todayDate}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        for trx in myresult:
                            if trx[1]==accounts:
                                ori_sum_debit+=trx[4]
                            else:
                                ori_sum_credit+=trx[4]
                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date='{todayDate}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        sum_debit, sum_credit = 0, 0
                        if ori_sum_debit>ori_sum_credit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", format_string(ori_sum_debit-ori_sum_credit), ""], divider=True)
                            sum_debit+=ori_sum_debit-ori_sum_credit
                        elif ori_sum_credit>ori_sum_debit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", "", format_string(ori_sum_credit-ori_sum_debit)], divider=True)
                            sum_credit+=ori_sum_credit-ori_sum_debit
                        for trx in myresult:
                            if trx[1]==accounts:
                                t.add_row([trx[0], trx[2], format_string(int(trx[4])), ""])
                                sum_debit+=trx[4]
                                pass
                            else:
                                t.add_row([trx[0], trx[1], "", format_string(int(trx[4]))])
                                sum_credit+=trx[4]
                                pass
                        if sum_debit>sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(sum_debit-sum_credit)], divider=True)
                            t.add_row(["", "Total", format_string(sum_debit), format_string(sum_debit)])

                        elif sum_debit<sum_credit:
                            t.add_row(["", "Balance c/d", format_string(sum_credit-sum_debit), ""], divider=True)
                            t.add_row(["", "Total", format_string(sum_credit), format_string(sum_credit)])

                        else:
                            t.add_row(["", "", "", ""], divider=True)
                            t.add_row(["", "", format_string(sum_debit), format_string(sum_credit)])
                    else:
                        if ori_sum_debit>ori_sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(ori_sum_debit-ori_sum_credit)], divider=True)
                        else:
                            t.add_row(["", "Balance c/d", format_string(ori_sum_credit-ori_sum_debit), ""], divider=True)
                    cls()
                    print(t)
                elif options=="Yesterday":
                    ori_sum_debit=ori_sum_credit=0
                    td = date.today()
                    todayDate = td-timedelta(days=1)
                    t.title=f"{accounts} Account from {todayDate} to {todayDate}"
                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date<'{todayDate}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        for trx in myresult:
                            if trx[1]==accounts:
                                ori_sum_debit+=trx[4]
                            else:
                                ori_sum_credit+=trx[4]
                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date='{todayDate}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        sum_debit, sum_credit = 0, 0
                        if ori_sum_debit>ori_sum_credit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", format_string(ori_sum_debit-ori_sum_credit), ""], divider=True)
                            sum_debit+=ori_sum_debit-ori_sum_credit
                        elif ori_sum_credit>ori_sum_debit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", "", format_string(ori_sum_credit-ori_sum_debit)], divider=True)
                            sum_credit+=ori_sum_credit-ori_sum_debit
                        for trx in myresult:
                            if trx[1]==accounts:
                                t.add_row([trx[0], trx[2], format_string(int(trx[4])), ""])
                                sum_debit+=trx[4]
                                pass
                            else:
                                t.add_row([trx[0], trx[1], "", format_string(int(trx[4]))])
                                sum_credit+=trx[4]
                                pass
                        if sum_debit>sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(sum_debit-sum_credit)], divider=True)
                            t.add_row(["", "Total", format_string(sum_debit), format_string(sum_debit)])

                        elif sum_debit<sum_credit:
                            t.add_row(["", "Balance c/d", format_string(sum_credit-sum_debit), ""], divider=True)
                            t.add_row(["", "Total", format_string(sum_credit), format_string(sum_credit)])

                        else:
                            t.add_row(["", "", "", ""], divider=True)
                            t.add_row(["", "", format_string(sum_debit), format_string(sum_credit)])
                    else:
                        if ori_sum_debit>ori_sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(ori_sum_debit-ori_sum_credit)], divider=True)
                        else:
                            t.add_row(["", "Balance c/d", format_string(ori_sum_credit-ori_sum_debit), ""], divider=True)
                    cls()
                    print(t)
                elif options=="This Week":
                    ori_sum_debit=ori_sum_credit=0
                    start_of_week = datetime.now() - timedelta(days=datetime.now().weekday())
                    end_of_week = start_of_week + timedelta(days=6)
                    t.title=f"{accounts} Account for the week {start_of_week.date()} to {end_of_week.date()}"
                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date<'{start_of_week}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        for trx in myresult:
                            if trx[1]==accounts:
                                ori_sum_debit+=trx[4]
                            else:
                                ori_sum_credit+=trx[4]

                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date between '{start_of_week}' and '{end_of_week}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        sum_debit, sum_credit = 0, 0
                        if ori_sum_debit>ori_sum_credit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", format_string(ori_sum_debit-ori_sum_credit), ""], divider=True)
                            sum_debit+=ori_sum_debit-ori_sum_credit
                        elif ori_sum_credit>ori_sum_debit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", "", format_string(ori_sum_credit-ori_sum_debit)], divider=True)
                            sum_credit+=ori_sum_credit-ori_sum_debit
                        for trx in myresult:
                            if trx[1]==accounts:
                                t.add_row([trx[0], trx[2], format_string(int(trx[4])), ""])
                                sum_debit+=trx[4]
                                pass
                            else:
                                t.add_row([trx[0], trx[1], "", format_string(int(trx[4]))])
                                sum_credit+=trx[4]
                                pass
                        if sum_debit>sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(sum_debit-sum_credit)], divider=True)
                            t.add_row(["", "Total", format_string(sum_debit), format_string(sum_debit)])

                        elif sum_debit<sum_credit:
                            t.add_row(["", "Balance c/d", format_string(sum_credit-sum_debit), ""], divider=True)
                            t.add_row(["", "Total", format_string(sum_credit), format_string(sum_credit)])

                        else:
                            t.add_row(["", "", "", ""], divider=True)
                            t.add_row(["", "", format_string(sum_debit), format_string(sum_credit)])
                    else:
                        if ori_sum_debit>ori_sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(ori_sum_debit-ori_sum_credit)], divider=True)
                        else:
                            t.add_row(["", "Balance c/d", format_string(ori_sum_credit-ori_sum_debit), ""], divider=True)
                    cls()
                    print(t)
                elif options=="This Month":
                    ori_sum_debit=ori_sum_credit=0
                    start_of_month = datetime.now().replace(day=1)
                    end_of_month = datetime.now().replace(day=calendar.monthrange(datetime.now().year, datetime.now().month)[1])
                    t.title = f"{accounts} Account from {start_of_month.date()} to {end_of_month.date()}"
                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date<'{start_of_month}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        for trx in myresult:
                            if trx[1]==accounts:
                                ori_sum_debit+=trx[4]
                            else:
                                ori_sum_credit+=trx[4]

                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date between '{start_of_month}' and '{end_of_month}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        sum_debit, sum_credit = 0, 0
                        if ori_sum_debit>ori_sum_credit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", format_string(ori_sum_debit-ori_sum_credit), ""], divider=True)
                            sum_debit+=ori_sum_debit-ori_sum_credit
                        elif ori_sum_credit>ori_sum_debit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", "", format_string(ori_sum_credit-ori_sum_debit)], divider=True)
                            sum_credit+=ori_sum_credit-ori_sum_debit
                        for trx in myresult:
                            if trx[1]==accounts:
                                t.add_row([trx[0], trx[2], format_string(int(trx[4])), ""])
                                sum_debit+=trx[4]
                                pass
                            else:
                                t.add_row([trx[0], trx[1], "", format_string(int(trx[4]))])
                                sum_credit+=trx[4]
                                pass
                        if sum_debit>sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(sum_debit-sum_credit)], divider=True)
                            t.add_row(["", "Total", format_string(sum_debit), format_string(sum_debit)])

                        elif sum_debit<sum_credit:
                            t.add_row(["", "Balance c/d", format_string(sum_credit-sum_debit), ""], divider=True)
                            t.add_row(["", "Total", format_string(sum_credit), format_string(sum_credit)])

                        else:
                            t.add_row(["", "", "", ""], divider=True)
                            t.add_row(["", "", format_string(sum_debit), format_string(sum_credit)])
                    else:
                        if ori_sum_debit>ori_sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(ori_sum_debit-ori_sum_credit)], divider=True)
                        else:
                            t.add_row(["", "Balance c/d", format_string(ori_sum_credit-ori_sum_debit), ""], divider=True)
                    cls()
                    print(t)
                elif options=="Last Month":
                    ori_sum_debit=ori_sum_credit=0
                    end_of_month = datetime.now().replace(day=1) - timedelta(days=1)
                    start_of_month = end_of_month.replace(day=1)
                    t.title = f"{accounts} Account from {start_of_month.date()} to {end_of_month.date()}"
                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date<'{start_of_month}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        for trx in myresult:
                            if trx[1]==accounts:
                                ori_sum_debit+=trx[4]
                            else:
                                ori_sum_credit+=trx[4]

                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date between '{start_of_month}' and '{end_of_month}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        sum_debit, sum_credit = 0, 0
                        if ori_sum_debit>ori_sum_credit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", format_string(ori_sum_debit-ori_sum_credit), ""], divider=True)
                            sum_debit+=ori_sum_debit-ori_sum_credit
                        elif ori_sum_credit>ori_sum_debit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", "", format_string(ori_sum_credit-ori_sum_debit)], divider=True)
                            sum_credit+=ori_sum_credit-ori_sum_debit
                        for trx in myresult:
                            if trx[1]==accounts:
                                t.add_row([trx[0], trx[2], format_string(int(trx[4])), ""])
                                sum_debit+=trx[4]
                                pass
                            else:
                                t.add_row([trx[0], trx[1], "", format_string(int(trx[4]))])
                                sum_credit+=trx[4]
                                pass
                        if sum_debit>sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(sum_debit-sum_credit)], divider=True)
                            t.add_row(["", "Total", format_string(sum_debit), format_string(sum_debit)])

                        elif sum_debit<sum_credit:
                            t.add_row(["", "Balance c/d", format_string(sum_credit-sum_debit), ""], divider=True)
                            t.add_row(["", "Total", format_string(sum_credit), format_string(sum_credit)])

                        else:
                            t.add_row(["", "", "", ""], divider=True)
                            t.add_row(["", "", format_string(sum_debit), format_string(sum_credit)])
                    else:
                        if ori_sum_debit>ori_sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(ori_sum_debit-ori_sum_credit)], divider=True)
                        else:
                            t.add_row(["", "Balance c/d", format_string(ori_sum_credit-ori_sum_debit), ""], divider=True)
                    cls()
                    print(t)
                elif options=="Calender Year till date":
                    ori_sum_debit=ori_sum_credit=0
                    start_of_month = datetime.now().replace(month=1, day=1)
                    end_of_month = datetime.now()
                    t.title = f"{accounts} Account from {start_of_month.date()} to {end_of_month.date()}"
                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date<'{start_of_month}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        for trx in myresult:
                            if trx[1]==accounts:
                                ori_sum_debit+=trx[4]
                            else:
                                ori_sum_credit+=trx[4]
                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date between '{start_of_month}' and '{end_of_month}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        sum_debit, sum_credit = 0, 0
                        if ori_sum_debit>ori_sum_credit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", format_string(ori_sum_debit-ori_sum_credit), ""], divider=True)
                            sum_debit+=ori_sum_debit-ori_sum_credit
                        elif ori_sum_credit>ori_sum_debit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", "", format_string(ori_sum_credit-ori_sum_debit)], divider=True)
                            sum_credit+=ori_sum_credit-ori_sum_debit
                        for trx in myresult:
                            if trx[1]==accounts:
                                t.add_row([trx[0], trx[2], format_string(int(trx[4])), ""])
                                sum_debit+=trx[4]
                                pass
                            else:
                                t.add_row([trx[0], trx[1], "", format_string(int(trx[4]))])
                                sum_credit+=trx[4]
                                pass
                        if sum_debit>sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(sum_debit-sum_credit)], divider=True)
                            t.add_row(["", "Total", format_string(sum_debit), format_string(sum_debit)])

                        elif sum_debit<sum_credit:
                            t.add_row(["", "Balance c/d", format_string(sum_credit-sum_debit), ""], divider=True)
                            t.add_row(["", "Total", format_string(sum_credit), format_string(sum_credit)])

                        else:
                            t.add_row(["", "", "", ""], divider=True)
                            t.add_row(["", "", format_string(sum_debit), format_string(sum_credit)])
                    else:
                        if ori_sum_debit>ori_sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(ori_sum_debit-ori_sum_credit)], divider=True)
                        else:
                            t.add_row(["", "Balance c/d", format_string(ori_sum_credit-ori_sum_debit), ""], divider=True)
                    cls()
                    print(t)
                elif options=="Accounting Year till date":
                    ori_sum_debit=ori_sum_credit=0
                    months = {1:datetime.now().year-1, 2:datetime.now().year-1, 3:datetime.now().year-1}
                    if datetime.now().month in months:
                        start_of_month = datetime.now().replace(year=datetime.now().year - 1, month=4, day=1)
                    else:
                        start_of_month = datetime.now().replace(month=4, day=1)
                    end_of_month = datetime.now()
                    t.title = f"{accounts} Account from {start_of_month.date()} to {end_of_month.date()}"
                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date<'{start_of_month}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        for trx in myresult:
                            if trx[1]==accounts:
                                ori_sum_debit+=trx[4]
                            else:
                                ori_sum_credit+=trx[4]
                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date between '{start_of_month}' and '{end_of_month}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        sum_debit, sum_credit = 0, 0
                        if ori_sum_debit>ori_sum_credit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", format_string(ori_sum_debit-ori_sum_credit), ""], divider=True)
                            sum_debit+=ori_sum_debit-ori_sum_credit
                        elif ori_sum_credit>ori_sum_debit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", "", format_string(ori_sum_credit-ori_sum_debit)], divider=True)
                            sum_credit+=ori_sum_credit-ori_sum_debit
                        for trx in myresult:
                            if trx[1]==accounts:
                                t.add_row([trx[0], trx[2], format_string(int(trx[4])), ""])
                                sum_debit+=trx[4]
                                pass
                            else:
                                t.add_row([trx[0], trx[1], "", format_string(int(trx[4]))])
                                sum_credit+=trx[4]
                                pass
                        if sum_debit>sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(sum_debit-sum_credit)], divider=True)
                            t.add_row(["", "Total", format_string(sum_debit), format_string(sum_debit)])

                        elif sum_debit<sum_credit:
                            t.add_row(["", "Balance c/d", format_string(sum_credit-sum_debit), ""], divider=True)
                            t.add_row(["", "Total", format_string(sum_credit), format_string(sum_credit)])

                        else:
                            t.add_row(["", "", "", ""], divider=True)
                            t.add_row(["", "", format_string(sum_debit), format_string(sum_credit)])
                    else:
                        if ori_sum_debit>ori_sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(ori_sum_debit-ori_sum_credit)], divider=True)
                        else:
                            t.add_row(["", "Balance c/d", format_string(ori_sum_credit-ori_sum_debit), ""], divider=True)
                    cls()
                    print(t)
                elif options=="This Quarter":
                    ori_sum_debit=ori_sum_credit=0
                    today = datetime.now()
                    nearest_quarter_start = {1:1, 2:1, 3:1, 4:4, 5:4, 6:4, 7:7, 8:7, 9:7, 10:10, 11:10, 12:10}
                    nearest_quarter_end = {1:3, 2:3, 3:3, 4:6, 5:6, 6:6, 7:9, 8:9, 9:9, 10:12, 11:12, 12:12}
                    last_day = {3:31, 6:30, 9:30, 12:31}
                    start_of_month = today.replace(day=1, month=nearest_quarter_start[today.month])
                    end_of_month = today.replace(month=nearest_quarter_end[today.month], day=last_day[nearest_quarter_end[today.month]])
                    t.title = f"{accounts} Account from {start_of_month.date()} to {end_of_month.date()}"
                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date<'{start_of_month}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        for trx in myresult:
                            if trx[1]==accounts:
                                ori_sum_debit+=trx[4]
                            else:
                                ori_sum_credit+=trx[4]

                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date between '{start_of_month}' and '{end_of_month}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        sum_debit, sum_credit = 0, 0
                        if ori_sum_debit>ori_sum_credit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", format_string(ori_sum_debit-ori_sum_credit), ""], divider=True)
                            sum_debit+=ori_sum_debit-ori_sum_credit
                        elif ori_sum_credit>ori_sum_debit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", "", format_string(ori_sum_credit-ori_sum_debit)], divider=True)
                            sum_credit+=ori_sum_credit-ori_sum_debit
                        for trx in myresult:
                            if trx[1]==accounts:
                                t.add_row([trx[0], trx[2], format_string(int(trx[4])), ""])
                                sum_debit+=trx[4]
                                pass
                            else:
                                t.add_row([trx[0], trx[1], "", format_string(int(trx[4]))])
                                sum_credit+=trx[4]
                                pass
                        if sum_debit>sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(sum_debit-sum_credit)], divider=True)
                            t.add_row(["", "Total", format_string(sum_debit), format_string(sum_debit)])

                        elif sum_debit<sum_credit:
                            t.add_row(["", "Balance c/d", format_string(sum_credit-sum_debit), ""], divider=True)
                            t.add_row(["", "Total", format_string(sum_credit), format_string(sum_credit)])

                        else:
                            t.add_row(["", "", "", ""], divider=True)
                            t.add_row(["", "", format_string(sum_debit), format_string(sum_credit)])
                    else:
                        if ori_sum_debit>ori_sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(ori_sum_debit-ori_sum_credit)], divider=True)
                        else:
                            t.add_row(["", "Balance c/d", format_string(ori_sum_credit-ori_sum_debit), ""], divider=True)
                    cls()
                    print(t)
                elif options=="Last Quarter":
                    ori_sum_debit=ori_sum_credit=0
                    today = datetime.now()
                    nearest_quarter_start = {1:10, 2:10, 3:10, 4:1, 5:1, 6:1, 7:4, 8:4, 9:4, 10:7, 11:7, 12:7}
                    nearest_quarter_end = {1:12, 2:12, 3:12, 4:3, 5:3, 6:3, 7:6, 8:6, 9:6, 10:9, 11:9, 12:9}
                    last_day = {3:31, 6:30, 9:30, 12:31}
                    start_of_month = today.replace(day=1, month=nearest_quarter_start[today.month])
                    end_of_month = today.replace(month=nearest_quarter_end[today.month], day=last_day[nearest_quarter_end[today.month]])
                    if start_of_month.month in [10,11,12]:
                        year_ = start_of_month.year
                        start_of_month = start_of_month.replace(year=year_-1)
                        end_of_month = end_of_month.replace(year=year_-1)
                    t.title = f"{accounts} Account from {start_of_month.date()} to {end_of_month.date()}"
                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date<'{start_of_month}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        for trx in myresult:
                            if trx[1]==accounts:
                                ori_sum_debit+=trx[4]
                            else:
                                ori_sum_credit+=trx[4]
                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date between '{start_of_month}' and '{end_of_month}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        sum_debit, sum_credit = 0, 0
                        if ori_sum_debit>ori_sum_credit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", format_string(ori_sum_debit-ori_sum_credit), ""], divider=True)
                            sum_debit+=ori_sum_debit-ori_sum_credit
                        elif ori_sum_credit>ori_sum_debit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", "", format_string(ori_sum_credit-ori_sum_debit)], divider=True)
                            sum_credit+=ori_sum_credit-ori_sum_debit
                        for trx in myresult:
                            if trx[1]==accounts:
                                t.add_row([trx[0], trx[2], format_string(int(trx[4])), ""])
                                sum_debit+=trx[4]
                                pass
                            else:
                                t.add_row([trx[0], trx[1], "", format_string(int(trx[4]))])
                                sum_credit+=trx[4]
                                pass
                        if sum_debit>sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(sum_debit-sum_credit)], divider=True)
                            t.add_row(["", "Total", format_string(sum_debit), format_string(sum_debit)])

                        elif sum_debit<sum_credit:
                            t.add_row(["", "Balance c/d", format_string(sum_credit-sum_debit), ""], divider=True)
                            t.add_row(["", "Total", format_string(sum_credit), format_string(sum_credit)])

                        else:
                            t.add_row(["", "", "", ""], divider=True)
                            t.add_row(["", "", format_string(sum_debit), format_string(sum_credit)])
                    else:
                        if ori_sum_debit>ori_sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(ori_sum_debit-ori_sum_credit)], divider=True)
                        else:
                            t.add_row(["", "Balance c/d", format_string(ori_sum_credit-ori_sum_debit), ""], divider=True)
                    # cls()
                    print(t)
                else:
                    ori_sum_debit=ori_sum_credit=0
                    start_date = input("Enter the start date in YYYY-MM-DD format, include the dashes in between")
                    end_date = input("Enter the end date in YYYY-MM-DD format, include the dashes in between")
                    t.title = f"{accounts} Account for the Range {start_date}-{end_date}"
                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date<'{start_date}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        for trx in myresult:
                            if trx[1]==accounts:
                                ori_sum_debit+=trx[4]
                            else:
                                ori_sum_credit+=trx[4]
                    mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date between '{start_date}' and '{end_date}') order by trx_date")
                    myresult = mycursor.fetchall()
                    if myresult!=[]:
                        sum_debit, sum_credit = 0, 0
                        if ori_sum_debit>ori_sum_credit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", format_string(ori_sum_debit-ori_sum_credit), ""], divider=True)
                            sum_debit+=ori_sum_debit-ori_sum_credit
                        elif ori_sum_credit>ori_sum_debit and ori_sum_credit!=0:
                            t.add_row(["", "Balance b/d", "", format_string(ori_sum_credit-ori_sum_debit)], divider=True)
                            sum_credit+=ori_sum_credit-ori_sum_debit
                        for trx in myresult:
                            if trx[1]==accounts:
                                t.add_row([trx[0], trx[2], format_string(int(trx[4])), ""])
                                sum_debit+=trx[4]
                                pass
                            else:
                                t.add_row([trx[0], trx[1], "", format_string(int(trx[4]))])
                                sum_credit+=trx[4]
                                pass
                        if sum_debit>sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(sum_debit-sum_credit)], divider=True)
                            t.add_row(["", "Total", format_string(sum_debit), format_string(sum_debit)])

                        elif sum_debit<sum_credit:
                            t.add_row(["", "Balance c/d", format_string(sum_credit-sum_debit), ""], divider=True)
                            t.add_row(["", "Total", format_string(sum_credit), format_string(sum_credit)])

                        else:
                            t.add_row(["", "", "", ""], divider=True)
                            t.add_row(["", "", format_string(sum_debit), format_string(sum_credit)])
                    else:
                        if ori_sum_debit>ori_sum_credit:
                            t.add_row(["", "Balance c/d", "", format_string(ori_sum_debit-ori_sum_credit)], divider=True)
                        else:
                            t.add_row(["", "Balance c/d", format_string(ori_sum_credit-ori_sum_debit), ""], divider=True)
                    cls()
                    print(t)
    elif option=="Journal":
        cls()
        print("Note! Finex supports only Simple Journal Entries now. We'll introduce support for Compound Journal Entries in the future\n\n")
        mycursor.execute(f"SELECT account_name from coa where orgID={orgData[0][0]}")
        myresult=mycursor.fetchall()
        accounts = []
        if myresult==[]:
            print("You have not created any Ledger Account. Create an account to pass a journal entry")
            continue
        else:
            for account in myresult:
                accounts.append(account[0])
            date_ = input("Enter the date of the transaction in YYYY-MM-DD format, including the dashes")
            print("Select the account to be debited")
            debit_acc = accounts[cutie.select(accounts)]
            accounts.remove(debit_acc)
            print("Select the account to be credited")
            credit_acc = accounts[cutie.select(accounts)]
            narration = input("Enter a narration for the transaction (OPTIONAL)")
            amount = float(input("Enter the amount of the transaction"))
            mycursor.execute(f"SELECT max(trx_id) from journal where orgID={orgData[0][0]}")
            trx_id = mycursor.fetchall()[0][0]
            if trx_id==None:
                trx_id=1
            else:
                trx_id+=1

            mycursor.execute(f"INSERT INTO journal VALUES({orgData[0][0]}, '{date_}', '{debit_acc}', '{credit_acc}', '{narration}', {amount}, {trx_id})")
            con.commit()
            cls()
            print("Journalised successfully!\n")
    elif option=="Fixed Assets Management":
        fa_management("")
    elif option=="Exit":
        exit()
    elif option=="Financial Reports":
        cls()
        print("Select a financial report")
        reports = ["Trial Balance", "Trading and Profit & Loss Account", "Balance Sheet"]
        report = reports[cutie.select(reports)]
        if report=="Trial Balance":
            tot_debit=tot_credit = 0
            months = {1:datetime.now().year-1, 2:datetime.now().year-1, 3:datetime.now().year-1}
            if datetime.now().month in months:
                start_of_month = datetime.now().replace(year=datetime.now().year - 1, month=4, day=1)
            else:
                start_of_month = datetime.now().replace(month=4, day=1)
            end_of_month = datetime.now()
            mycursor.execute(f"SELECT account_name from coa where orgID={orgData[0][0]}")
            myresult=mycursor.fetchall()
            account_list = []
            t = prettytable.PrettyTable()
            t.field_names=["Particulars", "Dr.", "Cr."]
            t.title = f"Trial Balance from {start_of_month.date()} to {end_of_month.date()}"
            for account in myresult:
                account_list.append(account[0])
            for accounts in account_list:
                ori_sum_debit=0
                ori_sum_credit=0
                mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date<'{start_of_month}') order by trx_date")
                myresult = mycursor.fetchall()
                if myresult!=[]:
                    for trx in myresult:
                        if trx[1]==accounts:
                            ori_sum_debit+=trx[4]
                        else:
                            ori_sum_credit+=trx[4]
                mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date between '{start_of_month}' and '{end_of_month}') order by trx_date")
                myresult = mycursor.fetchall()
                if myresult!=[]:
                    sum_debit, sum_credit = 0, 0
                    if ori_sum_debit>ori_sum_credit and ori_sum_credit!=0:
                        sum_debit+=ori_sum_debit-ori_sum_credit
                    elif ori_sum_credit>ori_sum_debit and ori_sum_credit!=0:
                        sum_credit+=ori_sum_credit-ori_sum_debit
                    for trx in myresult:
                        if trx[1]==accounts:
                            sum_debit+=trx[4]
                            pass
                        else:
                            sum_credit+=trx[4]
                            pass
                    if sum_debit>sum_credit:
                        balance = sum_debit-sum_credit
                        t.add_row([accounts, balance, ""])
                        tot_debit+=balance
                    elif sum_debit<sum_credit:
                        balance = sum_credit-sum_debit
                        tot_credit+=balance
                        t.add_row([accounts, "", balance])
                else:
                    if ori_sum_debit>ori_sum_credit:
                        balance = ori_sum_debit-ori_sum_credit
                        t.add_row([accounts, balance, ""])
                        tot_debit+=balance
                    elif ori_sum_debit==ori_sum_credit:
                        pass
                    else:
                        balance = ori_sum_credit-ori_sum_debit
                        t.add_row([accounts, "", balance])
                        tot_credit+=balance
            t.add_row(["", "", ""], divider=True)
            t.add_row(["Total", tot_debit, tot_credit])   
            cls()
            print(t)    
            choice = cutie.prompt_yes_or_no("Export the Trial Balance to a CSV File")
            if choice==True:
                with open("tb.csv", 'w', newline='') as f_output:
                    f_output.write(t.get_csv_string())
                print("Exported successfully!")
                path = f"{os.getcwd()}/tb.csv"
                print(f"File path: {path}")
        elif report=="Trading and Profit & Loss Account":
            months = {1:datetime.now().year-1, 2:datetime.now().year-1, 3:datetime.now().year-1}
            if datetime.now().month in months:
                start_of_month = datetime.now().replace(year=datetime.now().year - 1, month=4, day=1)
            else:
                start_of_month = datetime.now().replace(month=4, day=1)
            end_of_month = datetime.now()
            t = prettytable.PrettyTable()
            t.field_names=["Expenses", "Amount", "Incomes", " Amount "]
            today = datetime.now()
            if today.month==3 and today.date==31:
                t.title = f"Trading and Profit & Loss Account for the year ended {today.year-1}-{today.year}"
            else:
                t.title = f"Trading and Profit & Loss Account from {start_of_month.date()}-{end_of_month.date()}"
            mycursor.execute(f"SELECT account_name from coa where orgID={orgData[0][0]} and category in ('DE', 'DI')")
            myresult=mycursor.fetchall()
            account_list = []
            for account in myresult:
                account_list.append(account[0])
            tot_debit = tot_credit = 0
            for accounts in account_list:
                ori_sum_debit=0
                ori_sum_credit=0
                mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date<'{start_of_month}') order by trx_date")
                myresult = mycursor.fetchall()
                if myresult!=[]:
                    for trx in myresult:
                        if trx[1]==accounts:
                            ori_sum_debit+=trx[4]
                        else:
                            ori_sum_credit+=trx[4]
                mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date between '{start_of_month}' and '{end_of_month}') order by trx_date")
                myresult = mycursor.fetchall()
                if myresult!=[]:
                    sum_debit, sum_credit = 0, 0
                    if ori_sum_debit>ori_sum_credit and ori_sum_credit!=0:
                        sum_debit+=ori_sum_debit-ori_sum_credit
                    elif ori_sum_credit>ori_sum_debit and ori_sum_credit!=0:
                        sum_credit+=ori_sum_credit-ori_sum_debit
                    for trx in myresult:
                        if trx[1]==accounts:
                            sum_debit+=trx[4]
                            pass
                        else:
                            sum_credit+=trx[4]
                            pass
                    if sum_debit>sum_credit:
                        balance = sum_debit-sum_credit
                        t.add_row([accounts, balance, "", ""])
                        tot_debit+=balance
                    elif sum_debit<sum_credit:
                        balance = sum_credit-sum_debit
                        tot_credit+=balance
                        t.add_row(["", "", accounts, balance])
                else:
                    if ori_sum_debit>ori_sum_credit:
                        balance = ori_sum_debit-ori_sum_credit
                        t.add_row([accounts, balance, "", ""])
                        tot_debit+=balance
                    elif ori_sum_debit==ori_sum_credit:
                        pass
                    else:
                        balance = ori_sum_credit-ori_sum_debit
                        t.add_row(["", "", accounts, balance])
                        tot_credit+=balance
            if tot_credit>tot_debit:
                t.add_row(["Gross Profit c/d", tot_credit-tot_debit, "", ""], divider=True)
                t.add_row(["", tot_credit, "", tot_credit], divider=True)
                gross_profit = tot_credit-tot_debit
                t.add_row(["", "", "Gross Profit b/d", tot_credit-tot_debit])
            elif tot_debit>tot_credit:
                t.add_row(["", "", "Gross Loss c/d", tot_debit-tot_credit], divider=True)
                t.add_row(["", tot_debit, "", tot_debit], divider=True)
                t.add_row(["Gross Loss b/d", tot_debit-tot_credit, "", ""])
                gross_profit = tot_debit-tot_credit
            tot_debit=tot_credit=0
            mycursor.execute(f"SELECT account_name from coa where orgID={orgData[0][0]} and category in ('IE', 'II')")
            myresult=mycursor.fetchall()
            account_list = []
            for account in myresult:
                account_list.append(account[0])
            for accounts in account_list:
                print(accounts)
                ori_sum_debit=0
                ori_sum_credit=0
                mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date<'{start_of_month}') order by trx_date")
                myresult = mycursor.fetchall()
                if myresult!=[]:
                    for trx in myresult:
                        if trx[1]==accounts:
                            ori_sum_debit+=trx[4]
                        else:
                            ori_sum_credit+=trx[4]
                mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date between '{start_of_month}' and '{end_of_month}') order by trx_date")
                myresult = mycursor.fetchall()
                if myresult!=[]:
                    sum_debit, sum_credit = 0, 0
                    if ori_sum_debit>ori_sum_credit and ori_sum_credit!=0:
                        sum_debit+=ori_sum_debit-ori_sum_credit
                    elif ori_sum_credit>ori_sum_debit and ori_sum_credit!=0:
                        sum_credit+=ori_sum_credit-ori_sum_debit
                    for trx in myresult:
                        if trx[1]==accounts:
                            sum_debit+=trx[4]
                            pass
                        else:
                            sum_credit+=trx[4]
                            pass
                    if sum_debit>sum_credit:
                        balance = sum_debit-sum_credit
                        t.add_row([accounts, balance, "", ""])
                        tot_debit+=balance
                    elif sum_debit<sum_credit:
                        balance = sum_credit-sum_debit
                        tot_credit+=balance
                        t.add_row(["", "", accounts, balance])
                else:
                    if ori_sum_debit>ori_sum_credit:
                        balance = ori_sum_debit-ori_sum_credit
                        t.add_row([accounts, balance, "", ""])
                        tot_debit+=balance
                    elif ori_sum_debit==ori_sum_credit:
                        pass
                    else:
                        balance = ori_sum_credit-ori_sum_debit
                        t.add_row(["", "", accounts, balance])
                        tot_credit+=balance
            if tot_credit>tot_debit:
                t.add_row(["Net Profit t/d to Capital account", tot_credit-tot_debit, "", ""], divider=True)
                t.add_row(["", tot_credit, "", tot_credit], divider=True)
            elif tot_debit>tot_credit:
                t.add_row(["", "", "Net Loss t/d to Capital account", tot_debit-tot_credit], divider=True)
                t.add_row(["", tot_debit, "", tot_debit], divider=True)
            else:
                if gross_profit<0:
                    t.add_row(["", "", "Net Loss t/d to Capital account", -gross_profit], divider=True)
                    t.add_row(["", -gross_profit, "", -gross_profit], divider=True)
                else:
                    t.add_row(["Net Profit t/d to Capital account", gross_profit, "", ""], divider=True)
                    t.add_row(["", gross_profit, "", gross_profit], divider=True)
            cls()
            print(t)    
            choice = cutie.prompt_yes_or_no("Export the Trading and Profit and Loss account to a CSV File")
            if choice==True:
                with open("tpl.csv", 'w', newline='') as f_output:
                    f_output.write(t.get_csv_string())
                print("Exported successfully!")
                path = f"{os.getcwd()}/tb.csv"
                print(f"File path: {path}")
        else:
            months = {1:datetime.now().year-1, 2:datetime.now().year-1, 3:datetime.now().year-1}
            if datetime.now().month in months:
                start_of_month = datetime.now().replace(year=datetime.now().year - 1, month=4, day=1)
            else:
                start_of_month = datetime.now().replace(month=4, day=1)
            end_of_month = datetime.now()
            t = prettytable.PrettyTable()
            t.field_names=["Liabilities", "Amount", "Assets", " Amount "]
            today = datetime.now()
            t.title = f"Balance Sheet as on {end_of_month.date()}"
            mycursor.execute(f"SELECT account_name from coa where orgID={orgData[0][0]} and category in ('DE', 'DI', 'IE', 'II')")
            myresult=mycursor.fetchall()
            account_list = []
            for account in myresult:
                account_list.append(account[0])
            tot_debit = tot_credit = 0
            for accounts in account_list:
                ori_sum_debit=0
                ori_sum_credit=0
                mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date<'{start_of_month}') order by trx_date")
                myresult = mycursor.fetchall()
                if myresult!=[]:
                    for trx in myresult:
                        if trx[1]==accounts:
                            ori_sum_debit+=trx[4]
                        else:
                            ori_sum_credit+=trx[4]
                mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date between '{start_of_month}' and '{end_of_month}') order by trx_date")
                myresult = mycursor.fetchall()
                if myresult!=[]:
                    sum_debit, sum_credit = 0, 0
                    if ori_sum_debit>ori_sum_credit and ori_sum_credit!=0:
                        sum_debit+=ori_sum_debit-ori_sum_credit
                    elif ori_sum_credit>ori_sum_debit and ori_sum_credit!=0:
                        sum_credit+=ori_sum_credit-ori_sum_debit
                    for trx in myresult:
                        if trx[1]==accounts:
                            sum_debit+=trx[4]
                            pass
                        else:
                            sum_credit+=trx[4]
                            pass
                    if sum_debit>sum_credit:
                        balance = sum_debit-sum_credit
                        tot_debit+=balance
                    elif sum_debit<sum_credit:
                        balance = sum_credit-sum_debit
                        tot_credit+=balance
                else:
                    if ori_sum_debit>ori_sum_credit:
                        balance = ori_sum_debit-ori_sum_credit
                        tot_debit+=balance
                    elif ori_sum_debit==ori_sum_credit:
                        pass
                    else:
                        balance = ori_sum_credit-ori_sum_debit
                        tot_credit+=balance
            net_profit = tot_credit-tot_debit
            mycursor.execute(f"SELECT account_name from coa where orgID={orgData[0][0]} and category in ('C')")
            myresult=mycursor.fetchall()
            account_list = []
            for account in myresult:
                account_list.append(account[0])
            tot_debit = tot_credit = 0
            for accounts in account_list:
                ori_sum_debit=0
                ori_sum_credit=0
                mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date<'{start_of_month}') order by trx_date")
                myresult = mycursor.fetchall()
                if myresult!=[]:
                    for trx in myresult:
                        if trx[1]==accounts:
                            ori_sum_debit+=trx[4]
                        else:
                            ori_sum_credit+=trx[4]
                mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date between '{start_of_month}' and '{end_of_month}') order by trx_date")
                myresult = mycursor.fetchall()
                if myresult!=[]:
                    sum_debit, sum_credit = 0, 0
                    if ori_sum_debit>ori_sum_credit and ori_sum_credit!=0:
                        sum_debit+=ori_sum_debit-ori_sum_credit
                    elif ori_sum_credit>ori_sum_debit and ori_sum_credit!=0:
                        sum_credit+=ori_sum_credit-ori_sum_debit
                    for trx in myresult:
                        if trx[1]==accounts:
                            sum_debit+=trx[4]
                            pass
                        else:
                            sum_credit+=trx[4]
                            pass
                    ori_capital_balance = sum_credit-sum_debit
                    tot_credit+=balance
                
                else:
                    ori_capital_balance = ori_sum_credit-ori_sum_debit
                    tot_credit+=balance
            capital_balance = ori_capital_balance+net_profit
            if net_profit>0:
                t.add_row([f"Capital ({ori_capital_balance}) + Net Profit ({net_profit})", capital_balance, "",""])
            else:
                t.add_row([f"Capital ({ori_capital_balance}) - Net Loss ({-net_profit})", capital_balance, "",""])
            mycursor.execute(f"SELECT account_name from coa where orgID={orgData[0][0]} and category in ('A', 'L')")
            myresult=mycursor.fetchall()
            account_list = []
            for account in myresult:
                account_list.append(account[0])
            tot_debit = tot_credit = 0
            for accounts in account_list:
                
                ori_sum_debit=0
                ori_sum_credit=0
                mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date<'{start_of_month}') order by trx_date")
                myresult = mycursor.fetchall()
                if myresult!=[]:
                    for trx in myresult:
                        if trx[1]==accounts:
                            ori_sum_debit+=trx[4]
                        else:
                            ori_sum_credit+=trx[4]
                mycursor.execute(f"SELECT trx_date, debit_account, credit_account, narration, amount, trx_id from journal where orgID={orgData[0][0]} and (debit_account='{accounts}' or credit_account='{accounts}') and (trx_date between '{start_of_month}' and '{end_of_month}') order by trx_date")
                myresult = mycursor.fetchall()
                if myresult!=[]:
                    sum_debit, sum_credit = 0, 0
                    if ori_sum_debit>ori_sum_credit and ori_sum_credit!=0:
                        sum_debit+=ori_sum_debit-ori_sum_credit
                    elif ori_sum_credit>ori_sum_debit and ori_sum_credit!=0:
                        sum_credit+=ori_sum_credit-ori_sum_debit
                    for trx in myresult:
                        if trx[1]==accounts:
                            sum_debit+=trx[4]
                            pass
                        else:
                            sum_credit+=trx[4]
                            pass
                    if sum_debit>sum_credit:
                        balance = sum_debit-sum_credit
                        tot_debit+=balance
                        t.add_row(["", "", accounts, balance])
                    elif sum_debit<sum_credit:
                        balance = sum_credit-sum_debit
                        tot_credit+=balance
                        t.add_row([accounts, balance, "", ""])
                else:
                    if ori_sum_debit>ori_sum_credit:
                        balance = ori_sum_debit-ori_sum_credit
                        tot_debit+=balance
                    else:
                        balance = ori_sum_credit-ori_sum_debit
                        tot_credit+=balance
            t.add_row(["", "", "", ""], divider=True)
            tot_credit+=capital_balance
            t.add_row(["", tot_credit, "", tot_debit], divider=True)
            cls()
            print(t)
            choice = cutie.prompt_yes_or_no("Export the Balance Sheet to a CSV File")
            if choice==True:
                with open("bs.csv", 'w', newline='') as f_output:
                    f_output.write(t.get_csv_string())
                print("Exported successfully!")
                path = f"{os.getcwd()}/tb.csv"
                print(f"File path: {path}")