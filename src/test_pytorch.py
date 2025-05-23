import torch

def test_pytorch():
    print("PyTorch 버전:", torch.__version__)
    print("CUDA 사용 가능:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("CUDA 버전:", torch.version.cuda)
        print("현재 사용 중인 GPU:", torch.cuda.get_device_name(0))
    
    # 간단한 텐서 연산 테스트
    x = torch.rand(5, 3)
    print("\n랜덤 텐서 생성 테스트:")
    print(x)

if __name__ == "__main__":
    test_pytorch() 