import numpy as np
import cv2
import easyocr

reader = easyocr.Reader(['ko'])

class Preprocess:

    def setData(self, img, org_pts):
        self.img = img
        self.org_pts = org_pts

    def Deskew(self, img):
        # img : 본 이미지(원본)
        # org_pts : 사용자가 지정한 point. 2차 list로 받는 걸로 생각함.
        rows, cols, _ = img.shape

        pts1 = np.float32([[self.org_pts[0][0], self.org_pts[0][1]], [self.org_pts[1][0], self.org_pts[1][1]],
                           [self.org_pts[2][0], self.org_pts[2][1]], [self.org_pts[3][0], self.org_pts[3][1]]])
        new_pts = []  # 확장할 점의 네 변수를 저장함

        # 왼쪽 x좌표
        if (pts1[0][0] >= pts1[2][0]):
            new_pts.append(pts1[2][0])
        else:
            new_pts.append(pts1[0][0])

        # 위 y좌표
        if (pts1[0][1] >= pts1[1][1]):
            new_pts.append(pts1[1][1])
        else:
            new_pts.append(pts1[0][1])

        # 아래 y좌표
        if (pts1[2][1] >= pts1[3][1]):
            new_pts.append(pts1[2][1])
        else:
            new_pts.append(pts1[3][1])

        # 오른쪽 x좌표
        if (pts1[1][0] >= pts1[3][0]):
            new_pts.append(pts1[1][0])
        else:
            new_pts.append(pts1[3][0])

        pts2 = np.float32(
            [[new_pts[0], new_pts[1]], [new_pts[3], new_pts[1]], [new_pts[0], new_pts[2]], [new_pts[3], new_pts[2]]])

        M = cv2.getPerspectiveTransform(pts1, pts2)
        dst = cv2.warpPerspective(img, M, (cols, rows))
        # image crop
        dst = dst[int(new_pts[1]):int(new_pts[2]), int(new_pts[0]):int(new_pts[3])]

        return dst

    def Despeckle(self, img):

        image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        se2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        erosion = cv2.erode(image, se2)

        se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        bg = cv2.morphologyEx(erosion, cv2.MORPH_DILATE, se)

        out_gray = cv2.divide(image, bg, scale=255)
        out_gray = cv2.cvtColor(out_gray, cv2.COLOR_GRAY2BGR)

        return out_gray

    def showResult(self, res):
        text = [res[i][1] for i in range(0, len(res))];
        result = ' '.join(text)
        return result

    def stepOne(self):
        dst = self.Deskew(self.img)
        bounds_pre = reader.readtext(dst)
        self.result1 = self.showResult(bounds_pre)

    def stepTwo(self):
        dst = self.Despeckle(self.img)
        dst2 = self.Deskew(dst)
        bounds_pre = reader.readtext(dst2)
        self.result2 = self.showResult(bounds_pre)

    def stepThree(self):
        # img = self.img
        dst = self.Deskew(self.img)
        dst2 = self.Despeckle(dst)
        bounds_pre = reader.readtext(dst2)
        self.result3 = self.showResult(bounds_pre)

    def allResult(self):
        prep_result = self.result1 + ", " + self.result2 + ", " + self.result3
        return prep_result

    def __init__(self, img, org_pts):
        self.setData(img, org_pts)
        self.stepOne()
        self.stepTwo()
        self.stepThree()
