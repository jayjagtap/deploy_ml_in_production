from efficient_net_classifier import Efn_classifier


if __name__ == "__main__":
    img_classification = Efn_classifier()
    preds = img_classification.get_predictions(file_path="dog.jpeg")
    print(f"Predictions for the image: ", preds)
