# 채식인을 위한 원재료명 OCR 웹 서비스 <Let’s Go Green>
---
<br> 2020년 9월 ~ 12월 진행한, 융합캡스톤디자인 과목 팀 프로젝트 <Let’s Go Green> 의 FE, BE 부분 백업용 레포지토리 입니다.
<br> (추후 readme 수정 예정입니다.)

### 프로젝트 목적

<Let’s Go Green> 프로젝트는 채식을 지향하는 사용자를 위한 서비스로,
사용자가 식품 포장지에 표기된 원재료명을 촬영하고, 자신의 채식 단계를 입력하면
해당 식품의 섭취 가능 여부를 알려주는 웹 어플리케이션입니다.

### 사용 기술
- FE 개발에 HTML, CSS, JavaScript를 사용하였고, 추가적인 화면 디자인에 Bootstrap을 이용하였습니다.
- FE, BE 개발을 위한 프레임워크로 Flask를 사용했습니다.

### 어플리케이션 모습

- index.html에서, 사용자에게 채식 단계 데이터와 원재료명 이미지를 입력 받습니다.
- back-end에서, 입력 받은 이미지를 해당 시간을 이름으로 하여 저장합니다.
- crop.html에서, 저장한 이미지 중 이미지 전처리에 필요한 원재료명 표 부분의 좌표를 클릭으로 입력 받습니다.
- back-end에서, 사용자의 채식 단계 데이터와 입력 받은 이미지, 원재료명 표 좌표를 넘겨 받아 전처리, 딥러닝 OCR, 후처리, database 대조를 통해 해당 식품의 섭취 가능 여부를 판별합니다.
- predict.html에서, 사용자에게 섭취 가능 여부를 출력하여 보여줍니다.

![그림2](https://user-images.githubusercontent.com/65700066/187595830-ff5fd5b4-b0b2-45f3-91b0-dcdc612fa3e9.png)
<img src = "https://user-images.githubusercontent.com/65700066/187595851-55667c6b-9703-44aa-a786-15fcbdf088a7.png" width = 600>
