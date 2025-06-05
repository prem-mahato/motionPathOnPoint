# Maya Motion Path Tool

This is a Python tool for Autodesk Maya that creates a motion path on a point **without shifting the object** to the curve's root position. It preserves the object's original transform.

## Features

- Creates a motionPath node
- Keeps object in place (no snap to curve start)
- Clean and easy to use script

## Screenshot / Demo

![Tool Demo](Screenshot.png)
![Tool Demo](demo.gif)

## Usage

1. Save the script as `motionPathOnPoint.py`
2. Use the following code in Maya's Script Editor:

```python
filePath = "F:/Script/motionPathOnPoint/motionPathOnPoint.py"  # Update path as needed
exec(open(filePath).read())
motionPath()
```
## Author
Prem Kumar Mahato
