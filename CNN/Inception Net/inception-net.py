#imports
import torch 
import torch.nn as nn

class conv_block(nn.Module):
    def __init__(self, in_channels,out_channels, **kwargs):
        super(conv_block,self).__init__()
        self.relu = nn.ReLU()
        self.conv = nn.Conv2d(in_channels,out_channels, **kwargs)
        self.batch_norm=nn.BatchNorm2d(out_channels)

    def forward(self,x):
        return self.relu(self.batch_norm(self.conv(x)))

class inception_block(nn.Module):
    def __init__(self, in_channel,out_1x1,red_3x3,out_3x3,red_5x5,out_5x5,out_1x1pool):
        super(inception_block,self).__init__()
        self.branch1=conv_block(in_channel,out_1x1,kernel_size=1)

        self.branch2=nn.Sequential(
            conv_block(in_channel,red_3x3,kernel_size=1),
            conv_block(red_3x3,out_3x3,kernel_size=3,stride=1,padding=1)
        )

        self.branch3=nn.Sequential(
            conv_block(in_channel,red_5x5,kernel_size=1),
            conv_block(red_5x5,out_5x5,kernel_size=5,stride=1,padding=2)
        )

        self.branch4 = nn.Sequential(
            nn.MaxPool2d(kernel_size=3, stride=1, padding=1),  
            conv_block(in_channel,out_1x1pool,kernel_size=1)
        )

    
    def forward(self,x):
        return torch.concat([self.branch1(x),self.branch2(x),self.branch3(x),self.branch4(x)],1)
    

class GoogLeNet(nn.Module):
    def __init__(self, in_channels=3,num_classes=1000):
        super(GoogLeNet,self).__init__()
        self.conv1=conv_block(in_channels=in_channels,out_channels=64,kernel_size=7,stride=2,padding=3)
        self.maxpool1 = nn.MaxPool2d(kernel_size=3,stride=2,padding=1)
        self.conv2 = conv_block(in_channels=64,out_channels=192,kernel_size=3,stride=1,padding=1)
        self.maxpool2 = nn.MaxPool2d(kernel_size=3,stride=2,padding=1)
        # in_channel,out_1x1,red_3x3,out_3x3,red_5x5,out_5x5,out_1x1pool
        self.inception3a = inception_block(192,64,96,128,16,32,32)
        self.inception3b = inception_block(256,128,128,192,32,96,64)
        self.maxpool3=nn.MaxPool2d(kernel_size=3,stride=2,padding=1)
        self.inception4a = inception_block(480,192,96,208,16,48,64)
        self.inception4b = inception_block(512,160,112,224,24,64,64)
        self.inception4c = inception_block(512,128,128,256,24,64,64)
        self.inception4d = inception_block(512,112,144,288,32,64,64)
        self.inception4e = inception_block(528,256,160,320,32,128,128)
        self.maxpool4 = nn.MaxPool2d(kernel_size=3,stride=2,padding=1)

        self.inception5a = inception_block(832,256,160,320,32,128,128)
        self.inception5b = inception_block(832,384,192,384,48,128,128)
        
        self.avgpool=nn.AvgPool2d(kernel_size=7,stride=1)
        self.dropout=nn.Dropout(0.4)
        self.fc1=nn.Linear(1024,1000)


    def forward(self,x):
        x=self.conv1(x)
        x=self.maxpool1(x)
        x=self.conv2(x)
        x=self.maxpool2(x)
        x=self.inception3a(x)
        x=self.inception3b(x)
        x=self.maxpool3(x)
        x=self.inception4a(x)
        x=self.inception4b(x)
        x=self.inception4c(x)
        x=self.inception4d(x)
        x=self.inception4e(x)
        x=self.maxpool4(x)
        x=self.inception5a(x)
        x=self.inception5b(x)
        x=self.avgpool(x)
        x=x.reshape(x.shape[0],-1)
        x=self.dropout(x)
        x=self.fc1(x)
        return x


from torchinfo import summary

if __name__ == '__main__':
    model = GoogLeNet(3, 1000)
    summary_str = str(summary(model, input_size=(3, 224, 224), verbose=2, batch_dim=0))

    # Write summary to Markdown file
    with open("model_summary.md", "w") as f:
        f.write("```text\n")  # Start code block for formatting in Markdown
        f.write(summary_str)
        f.write("\n```")  # End code block


