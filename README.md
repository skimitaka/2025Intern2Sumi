## パッケージのインストール

```
uv python pin 3.9
uv sync
uv add numpy jupyter matplotlib pandas scikit-learn GPy GPyOpt
uv sync
```

uv add GPyの時に、C++のBuild Toolsが言われるので、それもインストールしておく
https://visualstudio.microsoft.com/ja/visual-cpp-build-tools/

## 備忘録
```
uv python pin 3.11
```
エラーが出たら、pyproject.tomlを直接編集
```
requires-python = ">=3.9"
```
