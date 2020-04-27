import re

# keywords=['Agriculture','agriculture','agricultural','gricultural','ranch','Ranch','farm','Farm',
#           'farm fence installers','farm fence installer',]
keywords=['agriculture','agricultural','ranch','farm','farm fence installers','farm fence installer',]


def keyword_map(fl_single):
    try:
        tem_tags = []
        company_name=str(fl_single['Company/Title']).lower()
        Description_m=str(fl_single['Description']).lower()
        for par in keywords:
            if re.search(r'\b({})\b'.format(par), company_name) is not None or re.search(
                    r'\b({})\b'.format(par), Description_m) is not None:
                    tem_tags.append(par)
        fl_single["tags"]=[]
        if len(tem_tags):
            fl_single["tags"] = tem_tags.copy()
            print(f"Fence tags ==> {tem_tags}")
            return True
        return False
    except Exception as error:
        print(f"Error in getting tags from deails ==> {error}")