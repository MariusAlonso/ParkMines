from statistics import mean

#model = "ppo2_cartpole"


statics_1e3 = [-102418.58333333296, -57275.69444444447, -69067.62500000032, -90436.9861111123, -78757.58333333342, -107189.94444444514, -75083.86111111108, -69424.79166666688, -75329.58333333363, -84416.5555555558]
"mean_statics_1e3 = -80940"


#model = "ppo2_10e4"
statics_1e4 = [-20911.0833333333, -33280.40277777778, -39878.04166666667, -271837.8333333151, -39435.13888888887, -34800.541666666664, -29996.361111111106, -16485.652777777766, -38919.38888888888, -128009.4166666814]
"mean_statics_1e4 = -65355"

#model = "ppo2_10e5"
statics_1e6 = []
"mean_statics_1e6 = "




print(mean(statics_10e3), mean(statics_10e4))
