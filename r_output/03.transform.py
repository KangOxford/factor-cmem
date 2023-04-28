import pandas as pd
import numpy as np
from tqdm import tqdm
import warnings;warnings.simplefilter("ignore", category=FutureWarning)
from os import listdir;from os.path import isfile, join
from r_output import Config
from sklearn.metrics import r2_score


pd.set_option('display.max_columns', None)

def platform():
    import pandas as pd
    import numpy as np
    from tqdm import tqdm
    import warnings;
    warnings.simplefilter("ignore", category=FutureWarning)
    from os import listdir;
    from os.path import isfile, join
    from data import Config

    pd.set_option('display.max_columns', None)

    import platform  # Check the system platform
    if platform.system() == 'Darwin':
        print("Running on MacOS")
        data_path = Config.r_data_path
    elif platform.system() == 'Linux':
        print("Running on Linux")
        raise NotImplementedError
    else:
        print("Unknown operating system")

    onlyfiles = sorted([f for f in listdir(data_path) if isfile(join(data_path, f))])
    return data_path, onlyfiles


def get_predict():
    import platform # Check the system platform
    if platform.system() == 'Darwin':
        print("Running on MacOS")
        data_path = Config.r_output_datapath
        # out_path = Config.r_data_path
        # try:
        #     listdir(out_path)
        # except:
        #     import os;os.mkdir(out_path)
    elif platform.system() == 'Linux':
        print("Running on Linux")
        raise NotImplementedError
    else:print("Unknown operating system")

    onlyfiles = sorted([f for f in listdir(data_path) if isfile(join(data_path, f))])
    # pred = []
    info_list = []
    for i in tqdm(range(len(onlyfiles))):
        file = onlyfiles[i]
        symbol = file[10:-4]
        df = pd.read_csv(data_path + file,header=None)
        df.iloc[:,0] = (df.iloc[:,0]-27)//26
        df.columns = ['date'] + ["A"+str(i+1) for i in range(26)]
        groupped = df.groupby('date')
        diagonal_elements_list = []
        for index, item in groupped:
            item.set_index('date', inplace=True)
            diagonal_elements = np.diag(item.values)
            diagonal_elements_list.extend(diagonal_elements)
        info = pd.Series(diagonal_elements_list,name = symbol+"_pred")
        info_list.append(info)
    rst = pd.DataFrame(info_list).T
    return rst

def get_df():
    data_path, onlyfiles = platform()
    df_list = []
    for i in range(len(onlyfiles)):
        file = onlyfiles[i]
        df = pd.read_csv(data_path + file, sep='\t|\n', engine='python')
        df = df.loc[:,['date','bin','turnover']]
        df.columns = ['date','bin',file[:-4]]
        df_list.append(df)

    # merge all dataframes on 'date' and 'bin' columns, keeping only the last column of each dataframe
    merged = pd.concat([df.set_index(['date', 'bin']).iloc[:, -1] for df in df_list], axis=1, keys=range(len(df_list)))
    # reset index to get back 'date' and 'bin' as columns
    merged = merged.reset_index()
    merged.columns = ['date','bin'] + [file[:-4] for file in onlyfiles]
    rst = merged.iloc[26:, :].reset_index()
    rst.drop(['index'],inplace = True, axis = 1)
    assert rst.shape[0] // 26 == rst.shape[0] / 26
    return rst


def get_result_data():
    df1 = get_df()
    predict = get_predict()
    predict
    rst = pd.concat([df1,predict],axis=1)
    return rst


df = get_result_data()
_, onlyfiles = platform()
symbols = [file[:-4]for file in onlyfiles]
r2_dct={}
for symbol in symbols:
    print(symbol)
    gpd = df.groupby('date')
    r2lst= []
    for index, item in gpd:
        r2 = r2_score(item[symbol],item[symbol+'_pred'])
        r2lst.append(r2)
    r2_dct[symbol] = pd.Series(r2lst)
r2df = pd.DataFrame(r2_dct)
r2df.drop(['ACN'],axis=1,inplace=True)
r2df.index = df.date.drop_duplicates()

m1= r2df.mean(axis=0)
m2 = r2df.mean(axis=1)

import matplotlib.pyplot as plt
plt.plot()


