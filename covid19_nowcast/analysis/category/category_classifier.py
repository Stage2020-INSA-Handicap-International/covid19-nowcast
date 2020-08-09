from argparse import ArgumentParser
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from keras.preprocessing.sequence import pad_sequences
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from transformers import XLNetTokenizer, XLNetForSequenceClassification, AdamW
from tqdm import tqdm
import progressbar
import json

#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#model = XLNetForSequenceClassification.from_pretrained('xlnet-base-cased', num_labels=8)
#model.load_state_dict(torch.load('covid19_nowcast/trained_models/cat_weights.pth'))
#model.eval()

def flat_accuracy(preds, labels):  # A function to predict Accuracy
    correct = 0
    for i in range(0, len(labels)):
        if (preds[i] == labels[i]):
            correct += 1
    return (correct / len(labels)) * 100


def category_accuracy(preds, labels):  # A function to predict Accuracy by category
    acc_neg = 0
    acc_neut = 0
    acc_pos = 0
    neg = 0
    neut = 0
    pos = 0
    for i in range(0, len(labels)):
        if labels[i] == 0:
            neg += 1
            if preds[i] == labels[i]:
                acc_neg += 1
        if labels[i] == 1:
            neut += 1
            if preds[i] == labels[i]:
                acc_neut += 1
        if labels[i] == 2:
            pos += 1
            if preds[i] == labels[i]:
                acc_pos += 1
    return (acc_neg / neg) * 100, (acc_neut / neut) * 100, (acc_pos / pos) * 100


def evaluate(model, test_loader, device, flat=True):
    model.eval()  # Testing our Model
    acc = []
    lab = []
    t = 0
    for inp, lab1 in tqdm(test_loader):
        inp.to(device)
        lab1.to(device)
        t += lab1.size(0)
        outp1 = model(inp.to(device))
        [acc.append(p1.item()) for p1 in torch.argmax(outp1[0], axis=1).flatten()]
        [lab.append(z1.item()) for z1 in lab1]
    if flat:
        print("Total Examples : {} Accuracy {}".format(t, flat_accuracy(acc, lab)))
    else:
        acc_neg, acc_neut, acc_pos = category_accuracy(acc, lab)
        print("Accuracy by category : neg {}, neut {}, pos {}".format(acc_neg, acc_neut, acc_pos))
    return flat_accuracy(acc, lab)


def test_sentence(w_path, device, pad, sentence, num_labels=8):
    model = XLNetForSequenceClassification.from_pretrained('xlnet-base-cased', num_labels=num_labels)
    model.load_state_dict(torch.load(w_path))
    model.eval()
    # prepare the sentence
    sentence_pr = sentence + "[SEP] [CLS]"
    tokenizer = XLNetTokenizer.from_pretrained('xlnet-base-cased', do_lower_case=True)
    tokenized_text = [tokenizer.tokenize(sentence_pr)]
    ids = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_text]
    # input_ids2 = pad_sequences(ids, dtype="long", truncating="post", padding="post")
    inp = torch.tensor(ids)
    outp1 = model(inp.to(device))
    print(sentence)
    # print(outp1)
    for p1 in torch.argmax(outp1[0], axis=1).flatten():
        print(p1.item())


def test_file(w_path, test_loader, device, model, flat=True):
    model.load_state_dict(torch.load(w_path))
    model.eval()
    acc = []
    lab = []
    t = 0
    pred = []
    for inp, lab1 in tqdm(test_loader):
        inp.to(device)
        lab1.to(device)
        t += lab1.size(0)
        outp1 = model(inp.to(device))
        [acc.append(p1.item()) for p1 in torch.argmax(outp1[0], axis=1).flatten()]
        [lab.append(z1.item()) for z1 in lab1]
        for p1 in torch.argmax(outp1[0], axis=1).flatten():
            if p1.item() == 0:
                pred.append('Business')
            elif p1.item() == 1:
                pred.append('Food')
            elif p1.item() == 2:
                pred.append('Health')
            elif p1.item() == 3:
                pred.append('Politics')
            elif p1.item() == 4:
                pred.append('Science')
            elif p1.item() == 5:
                pred.append('Sports')
            elif p1.item() == 6:
                pred.append('Tech')
            elif p1.item() == 7:
                pred.append('Travel')
    if flat:
        print("Total Examples : {} Accuracy {}".format(t, flat_accuracy(acc, lab)))
        return pred
    else:
        acc_neg, acc_neut, acc_pos = category_accuracy(acc, lab)
        print("Total Examples : {} Accuracy {}".format(t, flat_accuracy(acc, lab)))
        print("Accuracy by category : neg {}, neut {}, pos {}".format(acc_neg, acc_neut, acc_pos))
        conf_mat = confusion_matrix(lab, acc)
        true_neg = conf_mat[0][0]
        true_neut = conf_mat[1][1]
        true_pos = conf_mat[2][2]
        false_neg = conf_mat[1][0] + conf_mat[2][0]
        false_neut = conf_mat[0][1] + conf_mat[2][1]
        false_pos = conf_mat[0][2] + conf_mat[1][2]
        print("True negative: {}, True neutral: {}, True positive: {}".format(true_neg, true_neut, true_pos))
        print("False negative: {}, False neutral: {}, False positive: {}".format(false_neg, false_neut, false_pos))
        print("Precision negative: {}, Precision neutral: {}, Precision positive: {}".format(
            true_neg / (true_neg + false_neg), true_neut / (true_neut + false_neut), true_pos / (true_pos + false_pos)))
        return pred


def analyse(test_loader, device, model):

    pred = []
    for loader in progressbar.progressbar(test_loader, prefix="Categories: "):
        inp, label = loader
        outp1 = model(inp.to(device))
        for p1 in torch.argmax(outp1[0], axis=1).flatten():
            if p1.item() == 0:
                pred.append('Business')
            elif p1.item() == 1:
                pred.append('Food')
            elif p1.item() == 2:
                pred.append('Health')
            elif p1.item() == 3:
                pred.append('Politics')
            elif p1.item() == 4:
                pred.append('Science')
            elif p1.item() == 5:
                pred.append('Sports')
            elif p1.item() == 6:
                pred.append('Tech')
            elif p1.item() == 7:
                pred.append('Travel')

    return pred

def predict(data_to_predict, prediction_key):
    data=None
    if type(data_to_predict) is str:
        data = pd.read_json(data_to_predict)
    elif type(data_to_predict) is list:
        data = pd.DataFrame.from_dict(data_to_predict)
    else:
        raise TypeError("Unexpected type for data_to_predict: {}".format(type(data_to_predict).__name__))

    sentences = [sent for sent in data[prediction_key]]

    tokenizer = XLNetTokenizer.from_pretrained('xlnet-base-cased', do_lower_case=True)
    tokenized_text = [tokenizer.tokenize(sent) for sent in sentences]

    ids = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_text]

    labels = np.zeros(len(ids))

    # Getting max len in order to pad tokenized ids
    max1 = len(ids[0])
    for i in ids:
        if (len(i) > max1):
            max1 = len(i)
    # print(max1)
    MAX_LEN = max1

    input_ids2 = pad_sequences(ids, maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")

    Xtest = torch.tensor(input_ids2)
    Ytest = torch.tensor(labels)
    batch_size = 1
    test_data = TensorDataset(Xtest, Ytest)
    test_loader = DataLoader(test_data, batch_size=batch_size)

    data['category'] = analyse(test_loader, device, model)

    return data.to_dict(orient="records")


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument("-t", "--test", action="store_true")
    parser.add_argument("-a", "--analyse", action="store_true")
    parser.add_argument("-f", "--file", type=str, help="json file that will be used in the training or testing")
    parser.add_argument("-s", "--sentence", type=str, default="It's a pleasure to meet you")
    parser.add_argument("-op", "--option", type=str, default="preproc_text")
    parser.add_argument("-n", "--name", type=str, required=True)
    parser.add_argument("-e", "--epoch", type=int, default=10)
    parser.add_argument("-o", "--output", type=str, default="data_out.json")
    args = parser.parse_args()

    if args.analyse:
        assert (args.file)
        data = pd.read_json(args.file)
        # data = data.sample(frac=1) #Shuffle the dataset
        sentences = []
        for sentence in data[args.option]:
            sentences.append(sentence)

        tokenizer = XLNetTokenizer.from_pretrained('xlnet-base-cased', do_lower_case=True)
        tokenized_text = [tokenizer.tokenize(sent) for sent in sentences]

        ids = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_text]

        labels = np.zeros(len(ids))

        # Getting max len in order to pad tokenized ids
        max1 = len(ids[0])
        for i in ids:
            if (len(i) > max1):
                max1 = len(i)
        # print(max1)
        MAX_LEN = max1

        input_ids2 = pad_sequences(ids, maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")

        Xtest = torch.tensor(input_ids2)
        Ytest = torch.tensor(labels)
        batch_size = 1
        test_data = TensorDataset(Xtest, Ytest)
        test_loader = DataLoader(test_data, batch_size=batch_size)

        model = XLNetForSequenceClassification.from_pretrained('xlnet-base-cased', num_labels=8)
        data['pred'] = analyse(test_loader, device, model)

        data.to_json(args.output, orient='index', date_format='iso')
    elif args.test:
        if args.file:
            test_data = pd.read_json(args.file)
            test_data = test_data[['preproc_text', 'category', "full_text"]]
            test_data = test_data[test_data.category != "N/A"]
            test_data = test_data[test_data.category != "T Magazine"]
            test_data = test_data[test_data.category != "Magazine"]
            test_data = test_data[test_data.category != "Style"]
            test_data = test_data[test_data.category != "Books"]
            test_data = test_data[test_data.category != "N.Y."]
            test_data = test_data[test_data.category != "U.S."]
            test_data = test_data[test_data.category != "World"]
            test_data = test_data[test_data.category != "Opinion"]
            test_data = test_data[test_data.category != "Arts"]
            test_data = test_data[test_data.category != "Arts & Entertainment"]
            test_data = test_data[test_data.category != "LGBTQ"]
            test_data = test_data[test_data.category != "Reader"]
            sentences = []
            for sentence in test_data[args.option]:
                sentences.append(sentence)

            tokenizer = XLNetTokenizer.from_pretrained('xlnet-base-cased', do_lower_case=True)
            tokenized_text = [tokenizer.tokenize(sent) for sent in sentences]

            ids = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_text]

            #labels = test_data['category'].astype('category').cat.codes.values
            labels = np.zeros(len(ids))

            # Getting max len in order to pad tokenized ids
            max1 = len(ids[0])
            for i in ids:
                if (len(i) > max1):
                    max1 = len(i)
            # print(max1)
            MAX_LEN = max1

            input_ids2 = pad_sequences(ids, maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")

            Xtest = torch.tensor(input_ids2)
            Ytest = torch.tensor(labels)
            batch_size = 1
            test_dataset = TensorDataset(Xtest, Ytest)
            test_loader = DataLoader(test_dataset, batch_size=batch_size)

            model = XLNetForSequenceClassification.from_pretrained('xlnet-base-cased', num_labels=8)
            pred = test_file('cat_weights_{}_{}.pth'.format(args.option, args.name), test_loader, device, model,
                             flat=True)
            test_data['pred'] = pred
            # data = pd.concat([test_data, test_data], ignore_index=True, axis=1)
            test_data.to_json(args.output, orient='index', date_format='iso')
        else:
            test_sentence('cat_weights_{}_{}.pth'.format(args.option, args.name), device, 0, args.sentence)
    else:
        assert (args.file)
        data_train = pd.read_json(args.file)
        data_train = data_train[['preproc_text', 'category', 'full_text']]
        data_train = data_train[data_train.category != "N/A"]
        data_train = data_train[data_train.category != "T Magazine"]
        data_train = data_train[data_train.category != "Magazine"]
        data_train = data_train[data_train.category != "Style"]
        data_train = data_train[data_train.category != "Books"]
        data_train = data_train[data_train.category != "N.Y."]
        data_train = data_train[data_train.category != "U.S."]
        data_train = data_train[data_train.category != "World"]
        data_train = data_train[data_train.category != "Opinion"]
        data_train = data_train[data_train.category != "Arts"]
        data_train = data_train[data_train.category != "Arts & Entertainment"]
        data_train = data_train[data_train.category != "LGBTQ"]
        data_train = data_train[data_train.category != "Reader"]

        sentences = []
        for sentence in data_train[args.option]:
            sentences.append(sentence)

        tokenizer = XLNetTokenizer.from_pretrained('xlnet-base-cased', do_lower_case=True)
        tokenized_text = [tokenizer.tokenize(sent) for sent in sentences]

        ids = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_text]

        data_train['category_cat'] = data_train['category'].astype('category').cat.codes
        labels = data_train['category_cat'].values

        # Getting max len in order to pad tokenized ids
        max1 = len(ids[0])
        for i in ids:
            if (len(i) > max1):
                max1 = len(i)
        # print(max1)
        MAX_LEN = max1

        input_ids2 = pad_sequences(ids, maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")

        xtrain, xtest, ytrain, ytest = train_test_split(input_ids2, labels, test_size=0.25, random_state=69)

        Xtrain = torch.tensor(xtrain)
        Ytrain = torch.tensor(ytrain)
        Xtest = torch.tensor(xtest)
        Ytest = torch.tensor(ytest)

        batch_size = 3

        train_data = TensorDataset(Xtrain, Ytrain)
        test_data = TensorDataset(Xtest, Ytest)
        loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_data, batch_size=batch_size)

        model = XLNetForSequenceClassification.from_pretrained('xlnet-base-cased', num_labels=8)
        model.load_state_dict(torch.load("cat_weights_{}_{}.pth".format(args.option, args.name)))

        optimizer = AdamW(model.parameters(), lr=1e-6)

        criterion = nn.CrossEntropyLoss()

        no_train = 0
        epochs = args.epoch
        acc = 0
        for epoch in tqdm(range(epochs)):
            model.train()
            loss1 = []
            steps = 0
            train_loss = []
            l = []
            for inputs, labels1 in tqdm(loader):
                inputs.to(device)
                labels1 = labels1.long()
                labels1.to(device)
                optimizer.zero_grad()
                outputs = model(inputs.to(device))
                loss = criterion(outputs[0], labels1.to(device)).to(device)
                logits = outputs[0]
                # ll=outp(loss)
                [train_loss.append(p.item()) for p in torch.argmax(outputs[0], axis=1).flatten()]  # our predicted
                [l.append(z.item()) for z in labels1]  # real labels
                loss.backward()
                optimizer.step()
                loss1.append(loss.item())
                no_train += inputs.size(0)
                steps += 1
            print("Current Loss is : {} Step is : {} number of Example : {} Accuracy : {}".format(loss.item(), epoch,
                                                                                                  no_train,
                                                                                                  flat_accuracy(
                                                                                                      train_loss, l)))
            acc_eval = evaluate(model, test_loader, device, True)
            print("Eval accuracy : {}".format(acc_eval))
            if acc - acc_eval < 0:
                acc = acc_eval
                print("saving weights ...")
                torch.save(model.state_dict(), "cat_weights_{}_{}.pth".format(args.option, args.name))
        print("Saving last weights...")
        torch.save(model.state_dict(), "cat_weights_last_{}_{}.pth".format(args.option, args.name))
        print("Best eval accuracy : {}".format(acc))
