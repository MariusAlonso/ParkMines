
import numpy as np
import datetime
import random
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
from sklearn.utils import shuffle

mu_deposit_order = None
sigma_deposit_order = 12

mu_retrieval_order = None
sigma_retrieval_order = None

mu_stay_duration = None
sigma_stay_duration = None

mu_entrances = None
sigma_entrances = None

mu_exits = None
sigma_exits = None

def generate(flux_density=1, time=datetime.timedelta(days=31), start_date=datetime.date(2021, 1, 1)):

    movements = pd.DataFrame(columns = ["ORDER_DEPOSIT", "DEPOSIT", "ORDER_RETRIEVAL", "RETRIEVAL"])

