import math
from pyspark import SparkConf, SparkContext
from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel

def para_set(training_RDD,validation_for_predict_RDD):
    res_rank = []
    iterations = 5
    seed = 5L
    regularization_parameter = 0.1
    for rank in range(1,10):
        model = ALS.train(training_RDD, rank=rank, seed=seed, iterations=iterations, lambda_=regularization_parameter)
        predictions = model.predictAll(validation_for_predict_RDD).map(lambda r: ((r[0], r[1]), r[2]))
        rates_and_preds = validation_RDD.map(lambda r: ((int(r[0]), int(r[1])), float(r[2]))).join(predictions)
        error = math.sqrt(rates_and_preds.map(lambda r: (r[1][0] - r[1][1])**2).mean())
        print 'For rank %s the RMSE is %s' % (rank, error)
        res_rank.append((rank,error))
    best_rank = sorted(res_rank,key=lambda x:x[1])[0][0]
    res_iteration = []
    for iterations in range(2,20):
        model = ALS.train(training_RDD, rank=best_rank, seed=seed, iterations=iterations, lambda_=regularization_parameter)
        predictions = model.predictAll(validation_for_predict_RDD).map(lambda r: ((r[0], r[1]), r[2]))
        rates_and_preds = validation_RDD.map(lambda r: ((int(r[0]), int(r[1])), float(r[2]))).join(predictions)
        error = math.sqrt(rates_and_preds.map(lambda r: (r[1][0] - r[1][1])**2).mean())
        print 'For iteration %s the RMSE is %s' % (iterations, error)
        res_iteration.append((iterations,error))
    best_iteration = sorted(res_iteration,key=lambda x:x[1])[0][0]
    res_lambda = []
    for lambda_ in [i/10.0 for i in range(1,90)]:
        model = ALS.train(training_RDD, rank=best_rank, seed=seed, iterations=best_iteration, lambda_=lambda_)
        predictions = model.predictAll(validation_for_predict_RDD).map(lambda r: ((r[0], r[1]), r[2]))
        rates_and_preds = validation_RDD.map(lambda r: ((int(r[0]), int(r[1])), float(r[2]))).join(predictions)
        error = math.sqrt(rates_and_preds.map(lambda r: (r[1][0] - r[1][1])**2).mean())
        print 'For lambda %s the RMSE is %s' % (lambda_, error)
        res_lambda.append((lambda_,error))
    best_lambda = sorted(res_lambda,key=lambda x:x[1])[0][0]
    print best_iteration,best_rank,best_lambda
    return best_iteration,best_rank,best_lambda,res_rank,res_iteration,res_lambda

conf = SparkConf().setAppName("LYCA").set("spark.executor.memory", "8g")
sc = SparkContext(conf=conf)
# Load the complete dataset file
data = sc.textFile("data.csv")
header = data.take(1)[0]

# Parse
data = data.filter(lambda line: line!=header).map(lambda line: line.split(",")).map(lambda tokens: (tokens[0],tokens[1],tokens[2]))
training_RDD, validation_RDD, test_RDD= data.randomSplit([7, 2, 1], seed=0L)
validation_for_predict_RDD = validation_RDD.map(lambda x: (x[0], x[1]))
test_for_predict_RDD = test_RDD.map(lambda x: (x[0], x[1]))

iteration,rank,lambda_ = para_set(training_RDD,validation_for_predict_RDD)

model = ALS.train(training_RDD, rank=rank, seed=5L, iterations=iteration, lambda_=lambda_)
predictions = model.predictAll(validation_for_predict_RDD).map(lambda r: ((r[0], r[1]), r[2]))
rates_and_preds = validation_RDD.map(lambda r: ((int(r[0]), int(r[1])), float(r[2]))).join(predictions)
error = math.sqrt(rates_and_preds.map(lambda r: (r[1][0] - r[1][1])**2).mean())
model.save(sc, "CollaborativeFilter")

#sameModel = MatrixFactorizationModel.load(sc, "/tmp/data/myCollaborativeFilter")
