from writeToXlsx import WriteToXlsx


def main():
    print("yes")
    pamaster_path='./pamaster.xlsm'
    saved_path='./save.xlsx'
    XLSM = WriteToXlsx(pamaster_path, saved_path)

if __name__=='__main__':
    main()

