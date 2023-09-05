from tqdm import tqdm
import numpy as np
import pandas as pd
from os import listdir;
from os.path import isfile, join;
from sklearn.metrics import r2_score


import numpy as np
import pandas as pd
from tqdm import tqdm
import os;os.sys.path.append(os.path.expanduser('~') + "/cmem/codes/")
import os;os.sys.path.append(os.path.expanduser('~') + "/cmem/")
import os;os.sys.path.append("/homes/80/kang/cmem/")
import os;os.sys.path.append("/homes/80/kang/cmem/codes/")
from utils import *
from model import *
from params import *
from trainPred import *
import multiprocessing
import time

path060000Files = readFromPath(path060000)
print(len(path060000Files))


def getUniversalDf():
    # df = pd.read_csv(path0700+"universal.csv",index_col=0)
    return pd.read_pickle(path0700+"universal.pkl")
    # return pd.read_pickle(path0701+"one_file.pkl")


def get_r2df(num,regulator,df):
    
    print("universal data loaded")
    total_test_days, bin_size, train_size, test_size, x_list, y_list, original_space = param_define(df,num)
    print(f"num of stocks {num}, total test days {total_test_days}")
    # num_processes = multiprocessing.cpu_count()  # on local machine
    # num_processes = multiprocessing.cpu_count() -10 # on flair-node-03
    num_processes = 1 # Number of available CPU cores

    start = time.time()
    # with multiprocessing.Pool(processes=num_processes) as pool:
    r2results = [];oneday_dfs=[]
    print("total_test_days",total_test_days)
    for index in range(total_test_days):
        print(f"+ {index} in {total_test_days}")
        r2result,oneday_df = train_and_pred(index,df,num,regulator,tile_array=np.arange(num))
        r2results.append(r2result)
        oneday_dfs.append(oneday_df)
    end = time.time()
    
    def get_r2df_from_results(r2results):
        r2arr = np.array(r2results).reshape(-1, 3)
        df1 = pd.DataFrame(r2arr)
        df1.columns = ['test_date', 'stock_index', 'r2']
        # assert np.unique(df1['stock_index']).shape == (len(path060000Files),)
        df2 = df1.pivot(index="test_date", columns="stock_index", values="r2")
        return df2
    df2 = get_r2df_from_results(r2results)
    df22 =pd.concat(oneday_dfs,axis=0)

    print(f"time {(end-start)/60}")
    return df2, df22

def print_mean(df3):
    print(f">>>> stock mean: \n",df3.mean(axis=0))  # stock
    print(f">>>> date mean: \n",df3.mean(axis=1))   # date
    print(f">>>> aggregate mean: \n",df3.mean(axis=1).mean())

if __name__=="__main__":
    # regulator = "Lasso"
    # regulator = "XGB"

    # regulator = "cnnLstm"
    # regulator = "CNN"
    regulator = "OLS"
    # regulator = "Ridge"
    # regulator = "None"
    
    # df3 = get_r2df(num=1,regulator=regulator)
    num_of_stocks = len(path060000Files)
    df3,df33 = get_r2df(num=num_of_stocks,regulator=regulator,df = getUniversalDf())




    total_r2 = df3.mean(axis=1).mean()
    print('total r2: ',df3.mean(axis=1).mean()) # all mean
    df3.to_csv(path00 + "08_r2df_universal_day_"+str(num_of_stocks)+"_"+regulator+"_"+str(total_r2)[:6]+".csv", mode = 'w')
    df33.to_csv(path00 + "08_r2df_universal_day_"+str(num_of_stocks)+"_"+regulator+"_"+str(total_r2)[:6]+'_values_'+".csv", mode = 'w')
    
    