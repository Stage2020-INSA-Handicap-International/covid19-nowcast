from argparse import ArgumentParser
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from keras.preprocessing.sequence import pad_sequences
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from transformers import XLNetTokenizer, XLNetForSequenceClassification, AdamW
from tqdm import tqdm
import json

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def flat_accuracy(preds, labels):  # A function to predict Accuracy
    correct = 0
    for i in range(0, len(labels)):
        if (preds[i] == labels[i]):
            correct += 1
    return (correct / len(labels)) * 100

def sentiment_accuracy(preds, labels):  # A function to predict Accuracy by sentiment
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
    if flat :
        print("Total Examples : {} Accuracy {}".format(t, flat_accuracy(acc, lab)))
    else :
        acc_neg, acc_neut, acc_pos = sentiment_accuracy(acc, lab)
        print("Accuracy by sentiment : neg {}, neut {}, pos {}".format(acc_neg, acc_neut, acc_pos))
    return flat_accuracy(acc, lab)


def test_sentence(w_path, device, pad, sentence, num_labels=3):
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

def test_file(w_path, test_loader,  device, model, flat=True):
    model.load_state_dict(torch.load(w_path))
    model.eval()
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
        acc_neg, acc_neut, acc_pos = sentiment_accuracy(acc, lab)
        print("Accuracy by sentiment : neg {}, neut {}, pos {}".format(acc_neg, acc_neut, acc_pos))
    return flat_accuracy(acc, lab)

def analyse(w_path, test_loader, device, model, data, output_data_path):
    model.load_state_dict(torch.load(w_path))
    model.eval()
    pred = []
    for i, loader in tqdm(enumerate(test_loader)):
        inp, label = loader
        outp1 = model(inp.to(device))
        for p1 in torch.argmax(outp1[0], axis=1).flatten():
            if p1.item() == 0:
                pred.append('negative')
            elif p1.item() == 1:
                pred.append('neutral')
            elif p1.item() == 2:
                pred.append('positive')

    return pred




if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument("-t", "--test", action="store_true")
    parser.add_argument("-a", "--analyse", action="store_true")
    parser.add_argument("-f", "--file", type=str, help="json file that will be tested")
    parser.add_argument("-s", "--sentence", type=str, default="It's a pleasure to meet you")
    parser.add_argument("-op", "--option", type=str, default="full_text")
    parser.add_argument("-e", "--epoch", type=int, default=10)
    parser.add_argument("-o", "--output", type=str, default="data_out.json")
    args = parser.parse_args()

    if args.analyse :
        data = pd.read_json(args.file)
        sentences = []
        for sentence in data[args.option]:
            sentence = sentence + "[SEP] [CLS]"  # [SEP] and [CLS] is needed for our model
            sentences.append(sentence)

        tokenizer = XLNetTokenizer.from_pretrained('xlnet-base-cased', do_lower_case=True)
        tokenized_text = [tokenizer.tokenize(sent) for sent in sentences]

        ids = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_text]

        labels = data['sentiment'].astype('category').cat.codes.values

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

        model = XLNetForSequenceClassification.from_pretrained('xlnet-base-cased', num_labels=3)
        data['pred'] = analyse('xlnet_weights_full_text.pth', test_loader, device, model, data, args.output)

        data.to_json(args.output, orient='index', date_format='iso')
    elif args.test:
        if args.file :
            test_data = pd.read_json(args.file)
            test_data = test_data[['preproc_text', 'sentiment', 'full_text']]
            test_data = test_data[test_data.sentiment != "N/A"]
            # data_kenya = data_kenya[data_kenya.sentiment != "neutral"]
            test_data = test_data[test_data.sentiment != "mixed"]
            sentences = []
            for sentence in test_data[args.option]:
                sentence = sentence + "[SEP] [CLS]"  # [SEP] and [CLS] is needed for our model
                sentences.append(sentence)

            tokenizer = XLNetTokenizer.from_pretrained('xlnet-base-cased', do_lower_case=True)
            tokenized_text = [tokenizer.tokenize(sent) for sent in sentences]

            ids = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_text]

            test_data['sentiment_cat'] = test_data['sentiment'].astype('category').cat.codes
            labels = test_data['sentiment_cat'].values

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
            batch_size = 3
            test_data = TensorDataset(Xtest, Ytest)
            test_loader = DataLoader(test_data, batch_size=batch_size)

            model = XLNetForSequenceClassification.from_pretrained('xlnet-base-cased', num_labels=3)
            acc = test_file('xlnet_weights_full_text.pth', test_loader, device, model, flat=False)
            print("Total acc {}".format(acc))
        else :
            test_sentence('xlnet_weights_full_text.pth', device, 0, args.sentence)
    else:
        # data_kenya = pd.read_json('../../../Datasets/Kenya_tweets_sentiments.json')
        data_kenya = pd.read_json('../Kenya_tweets_sentiments.json')
        data_kenya = data_kenya[['preproc_text', 'sentiment', 'full_text']]
        data_kenya = data_kenya[data_kenya.sentiment != "N/A"]
        # data_kenya = data_kenya[data_kenya.sentiment != "neutral"]
        data_kenya = data_kenya[data_kenya.sentiment != "mixed"]
        # print(len(data_kenya['sentiment']))

        sentences = []
        for sentence in data_kenya[args.option]:
            sentence = sentence + "[SEP] [CLS]"  # [SEP] and [CLS] is needed for our model
            sentences.append(sentence)

        tokenizer = XLNetTokenizer.from_pretrained('xlnet-base-cased', do_lower_case=True)
        tokenized_text = [tokenizer.tokenize(sent) for sent in sentences]

        ids = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_text]

        data_kenya['sentiment_cat'] = data_kenya['sentiment'].astype('category').cat.codes
        labels = data_kenya['sentiment_cat'].values

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

        model = XLNetForSequenceClassification.from_pretrained('xlnet-base-cased', num_labels=3)

        optimizer = AdamW(model.parameters(), lr=2e-5)

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
            print("Current Loss is : {} Step is : {} number of Example : {} Accuracy : {}".format(loss.item(), epoch, no_train, flat_accuracy(train_loss, l)))
            acc_eval = evaluate(model, test_loader, device, False)
            print("Eval accuracy : {}".format(acc_eval))
            if acc - acc_eval < 0:
                acc = acc_eval
                print("saving weights ...")
                torch.save(model.state_dict(), "xlnet_weights_{}.pth".format(args.option))
        print("Saving last weights...")
        torch.save(model.state_dict(), "xlnet_weights_last_{}.pth".format(args.option))
        print("Best eval accuracy : {}".format(acc))
