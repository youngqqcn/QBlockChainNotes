
import requests
import json
# Create your tests here.

class SimpleTest():

    def __init__(self):

        pro_id = "15"
        tel_no = "15361022029"
        password = "88888888"
        new_password = "99999999."
        url = "http://127.0.0.1:8000"
        id = 70#提币配置id

        header = self.test_login(pro_id, tel_no, password, url)
        header = 'JWT ' + header
        headers = {"Authorization": header, "Content-Type": "application/json"}
        self.home(headers, url)
        self.Users(headers, url)
        self.WithdrawConfig(headers, url)
        self.WithdrawConfigPut(headers, url, id)
        self.CollectionFeeConfig(headers, url)
        self.CollectionConfig(headers, url)
        self.WithdrawOrder(headers, url)
        self.Deposit(headers, url)
        self.CollectionRecords(headers, url)
        self.Address(headers, url)
        self.UserAssets(headers, url)
        self.AssetDailyReport(headers, url)
        self.reset(headers=headers, pro_id=pro_id, tel_no=tel_no, password=password, new_password=new_password, url=url)


    def test_login(self, pro_id, tel_no, password,url):
        """
        登录请求参数:
            tel_no
            password
        :return:
        """
        data = {"pro_id": pro_id, "tel_no": tel_no, "password": password}
        response = requests.post(url=f'{url}/client/login/',data=json.dumps(data), headers={"Content-Type": "application/json"})
        token = json.loads(response.content)
        assert response.status_code == 200, Exception("login error")
        return token["token"]

    def home(self, headers, url):
        response = requests.get(url=f'{url}/client/', headers=headers)
        assert response.status_code == 200, Exception("home error")

    def Users(self, headers, url):
        response = requests.get(url=f'{url}/client/Users/', headers=headers)
        assert response.status_code == 200, Exception("Users error")

    def WithdrawConfig(self, headers, url):
        response = requests.get(url=f'{url}/client/WithdrawConfig/', headers=headers)
        assert response.status_code == 200, Exception("WithdrawConfig error")


    def WithdrawConfigPut(self, headers, url, id):
        id = id
        url = f'{url}/client/WithdrawConfig/{id}/'
        data = {
            "token_name": "HTDF",
            "min_amount": "0.001",
            "max_amount": "0.001",
            "balance_threshold_to_sms": "1"
        }
        response = requests.put(url, json.dumps(data), headers=headers)
        assert response.status_code == 200, Exception("WithdrawConfigPut error")

    def CollectionFeeConfig(self, headers, url):
        response = requests.get(url=f'{url}/client/CollectionFeeConfig/', headers=headers)
        assert response.status_code == 200, Exception("CollectionFeeConfig error")

    def CollectionConfig(self, headers, url):
        response = requests.get(url=f'{url}/client/CollectionConfig/', headers=headers)
        assert response.status_code == 200, Exception("CollectionConfig error")

    def WithdrawOrder(self, headers, url):
        response = requests.get(url=f'{url}/client/WithdrawOrder/', headers=headers)
        assert response.status_code == 200, Exception("WithdrawOrder error")

    def Deposit(self, headers, url):
        response = requests.get(url=f'{url}/client/Deposit/', headers=headers)
        assert response.status_code == 200, Exception("Deposit error")

    def CollectionRecords(self, headers, url):
        response = requests.get(url=f'{url}/client/CollectionRecords/', headers=headers)
        assert response.status_code == 200, Exception("CollectionRecords error")

    def Address(self, headers, url):
        response = requests.get(url=f'{url}/client/Address/', headers=headers)
        assert response.status_code == 200, Exception("Address error")

    def UserAssets(self, headers, url):
        response = requests.get(url=f'{url}/client/UserAssets/', headers=headers)
        assert response.status_code == 200, Exception("UserAssets error")

    def AssetDailyReport(self, headers, url):
        response = requests.get(url=f'{url}/client/AssetDailyReport/', headers=headers)
        assert response.status_code == 200, Exception("AssetDailyReport error")

    def reset(self, headers, password, tel_no, pro_id, new_password, url):
        data = {"new_password": new_password,
        "password_verify": new_password, "password":password, "pro_id":pro_id, "tel_no": tel_no}
        response = requests.put(f'{url}/client/reset/', json.dumps(data), headers=headers)
        assert response.status_code == 200, Exception("reset error")

if __name__ == '__main__':
    SimpleTest()