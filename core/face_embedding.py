from deepface.models.facial_recognition.Facenet import InceptionResNetV1
from deepface.models import FacialRecognition
# from deepface.commons import folder_utils
import os
import gdown

class FaceNet512dClient(FacialRecognition):
    """
    FaceNet-1512d model class
    """

    def __init__(self):
        self.model = self.load_facenet512d_model()
        self.model_name = "FaceNet-512d"
        self.input_shape = (160, 160)
        self.output_shape = 512

    def load_facenet512d_model(
        url="https://github.com/serengil/deepface_models/releases/download/v1.0/facenet512_weights.h5",
    ) -> Model:
        """
        Construct FaceNet-512d model, download its weights and load
        Returns:
            model (Model)
        """

        model = InceptionResNetV1(dimension=512)

        # -------------------------

        #home = folder_utils.get_deepface_home()
        #output = os.path.join(home, ".deepface/weights/facenet512_weights.h5")
        output = './models/image_embedding/facenet512_weights.h5'

        if not os.path.isfile(output):
            print(f"{os.path.basename(output)} will be downloaded...")
            gdown.download(url, output, quiet=False)

        # -------------------------

        model.load_weights(output)

        # -------------------------

        return model
