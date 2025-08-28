# Fastapi_example
For CV app entrance(in common use)

## 支援兩種輸入：
- JSON
```json
{
  "base64": "iVBORw0KGgoAAAANSUhEUgAA...", 
  "file_stream": [255, 216, 255, 224, 0, 16, 74, 70]
}
```
- File

```csharp
using var client = new HttpClient();
using var form = new MultipartFormDataContent();
form.Add(new StreamContent(File.OpenRead("sample.jpg")), "file", "sample.jpg");

var resp = await client.PostAsync("url", form);
Console.WriteLine(await resp.Content.ReadAsStringAsync());
```
```javascript
<input type="file" id="f">
<script>
async function send() {
  const fd = new FormData();
  fd.append("file", document.getElementById("f").files[0]);
  const r = await fetch("url", { method:"POST", body:fd });
  console.log(await r.json());
}
</script>
<button onclick="send()">Upload</button>
```

## 輸出範例：
```json
{
  "example_key_01": "example_value_01",
  "example_key_02": "example_value_02"
}
```
