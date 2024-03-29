from django.core.management import BaseCommand


from competition.models import CustomUser
from competition.utils.chess_utils import update_with_rcf

data = [[6, 0], [10, 0], [11, 0], [14, 0], [17, 0], [20, 0], [23, 80947], [24, 0], [26, 0], [27, 0], [28, 2246], [49, 0], [50, 0], [55, 0], [62, 0], [65, 33465], [70, 0], [73, 0], [75, 0], [77, 0], [78, 54066], [80, 74685], [82, 0], [83, 0], [86, 0], [87, 0], [88, 0], [89, 0], [90, 0], [91, 0], [92, 17385], [94, 277641], [95, 277641], [96, 0], [98, 0], [99, 0], [104, 0], [110, 247454], [114, 0], [115, 0], [117, 17809], [119, 0], [122, 218249], [123, 0], [126, 0], [127, 0], [129, 165361], [135, 0], [137, 0], [138, 0], [139, 205565], [141, 0], [146, 80146], [147, 0], [151, 0], [152, 0], [153, 412419], [155, 0], [156, 0], [158, 433298], [159, 0], [165, 0], [167, 240395], [171, 0], [172, 0], [173, 0], [174, 490221], [180, 0], [181, 0], [184, 0], [188, 160296], [192, 0], [199, 0], [205, 0], [206, 0], [207, 0], [209, 383237], [210, 0], [211, 20051], [212, 0], [217, 218249], [219, 0], [224, 0], [225, 61871], [231, 0], [233, 46991], [244, 0], [248, 3990], [249, 144145], [253, 0], [257, 0], [259, 0], [267, 0], [271, 0], [276, 28571], [286, 0], [287, 0], [293, 0], [295, 32433], [296, 320276], [297, 0], [298, 0], [299, 0], [300, 0], [302, 0], [304, 0], [305, 0], [306, 80603], [309, 53430], [311, 0], [315, 29796], [319, 13332], [320, 0], [321, 30446], [326, 0], [328, 0], [329, 0], [330, 0], [332, 0], [338, 0], [339, 224610], [340, 224610], [342, 0], [343, 0], [344, 0], [345, 0], [346, 229201], [347, 0], [348, 77386], [350, 83557], [351, 0], [352, 0], [353, 0], [354, 0], [356, 0], [358, 0], [359, 0], [363, 0], [367, 0], [368, 0], [369, 0], [371, 0], [372, 0], [373, 0], [374, 0], [377, 76069], [378, 0], [379, 0], [384, 65889], [385, 0], [389, 0], [391, 0], [395, 0], [399, 28464], [403, 0], [410, 0], [414, 177827], [416, 187404], [419, 144742], [422, 0], [423, 330172], [425, 0], [426, 83317], [428, 0], [430, 433341], [437, 0], [439, 0], [442, 0], [448, 0], [449, 0], [451, 406297], [452, 61738], [453, 0], [454, 33465], [455, 0], [456, 0], [457, 1446], [458, 0], [459, 0], [462, 0], [466, 0], [471, 0], [472, 167818], [481, 0], [486, 0], [488, 0], [492, 14058], [493, 0], [495, 27152], [498, 0], [499, 0], [502, 0], [505, 0], [507, 35129], [508, 0], [511, 0], [514, 0], [520, 0], [521, 0], [524, 189514], [528, 0], [534, 0], [535, 0], [536, 0], [537, 519766], [538, 0], [540, 0], [543, 14832], [544, 14832], [545, 218112], [546, 174905], [547, 0], [548, 0], [550, 159510], [551, 0], [552, 0], [555, 0], [557, 132650], [560, 0], [565, 0], [566, 169383], [570, 0], [571, 0], [572, 0], [573, 165073], [574, 0], [575, 0], [580, 0], [581, 0], [582, 0], [585, 158708], [586, 28782], [589, 0], [595, 0], [596, 206377], [603, 0], [615, 0], [618, 0], [619, 0], [621, 0], [623, 0]]

class Command(BaseCommand):
    help = "Updating gender of all users by the last letter of middle name"
    application_mode = False
    def handle(self, *args, **options):
        for data_piece in data:
            print(data_piece)
            user = CustomUser.objects.get(pk=data_piece[0])
            user.rf_id = data_piece[1]
            if data_piece[1]:
                found, rcf_data = update_with_rcf(user.rf_id)
                user.rf_id = int(rcf_data['rf_id'])

                if rcf_data.get('fide_id'):
                    user.fide_id = int(rcf_data['fide_id'])

                if rcf_data.get('rating_standart_ru'):
                    user.rating_standart_ru = int(rcf_data['rating_standart_ru'])

                if rcf_data.get('rating_rapid_ru'):
                    user.rating_rapid_ru = int(rcf_data['rating_rapid_ru'])

                if rcf_data.get('rating_blitz_ru'):
                    user.rating_blitz_ru = int(rcf_data['rating_blitz_ru'])

                if rcf_data.get('rating_standart'):
                    user.rating_standart = int(rcf_data['rating_standart'])

                if rcf_data.get('rating_rapid'):
                    user.rating_rapid = int(rcf_data['rating_rapid'])

                if rcf_data.get('rating_blitz'):
                    user.rating_blitz = int(rcf_data['rating_blitz'])

            user.save()
            print(f"User {user.email} ({user.rf_id=}) updated")