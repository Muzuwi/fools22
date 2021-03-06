# Fools22 API

### All packet commands must be be padded to a multiple of 32-bits

X-FoolsRefreshToken:	<token>

X-FoolsProtocolVersion:	    101

## /login

Request
```json
{"u": "<Username>", "p": "<password>"}
```

Response
```json
{
    "data": {
        "scope": "fools2022",
        "session": "<session-token>",
        "uid": 1111111
    },
    "error": 0
}
```

## /packet/$uid

X-Foolssessiontoken: token

Request is www-form-urlencoded

Response is plain (base64)

### Renewal

Request - 

```
BwAAAGhvbGRlcj1BZWxpdGEvdHlwZT1zaWx2ZXL/wEYIAAAA:
BwAAAGhvbGRlcj1BZWxpdGEvdHlwZT1zaWx2ZXL/wEYAAAAA:
```

```
BwAAAGhvbGRlcj1NdXp1d2kvdHlwZT1zaWx2ZXL/wEYAAAAA:
```

07000000686f6c6465723d4d757a7577692f747970653d73696c766572ffc04600000000

```
00000000  07 00 00 00 68 6f 6c 64  65 72 3d 41 65 6c 69 74  |....holder=Aelit|
00000010  61 2f 74 79 70 65 3d 73  69 6c 76 65 72 ff c0 46  |a/type=silver..F|
00000020  08 00 00 00                                       |....|
```

Response

```
SVRJbnAraGNTd2ZQMkM1cnZUQXl5Z2VDTTRUZi92NDdiVW02UWdIcWdVRU51TlRjc1ZGdlBBdGthRmFub2VJdUI0d04zbzNpYm5seHFzdFl0amxYVVE9Pf8=
SVRJbnAraGNTd2ZQMkM1cnZUQXl5Z2kvanFCaUxLVE8vb2ozekM1cTBzK3R5cm50MFRrYWsvOGgzSWVWbm11UC9pc1QreHI4d2FuWkx1U3pjZ0pMU2c9Pf8=
SVRJbnAraGNTd2ZQMkM1cnZUQXl5dUh3V1ppQkJ5bnNoRTdhaTAzUktFeVlHRHp1UlRCa3JrLzBKYXZraERudU1SVGpvVDAwZEh4Z3B5USszc3ErYUE9Pf8=
```

### Appraisal

Request:

```
CAAAAElUSW5wK2hjU3dmUDJDNXJ2VEF5eWdlQ000VGYvdjQ3YlVtNlFnSHFnVUVOdU5UY3NWRnZQQXRrYUZhbm9lSXVCNHdOM28zaWJubHhxc3RZdGpsWFVRPT3/AAAAAhcBgDcSEgDHHQICEwBlhwECFwGAAAASANp1AwITAIyHAQISANt1AwITAI2HAQIWAYAAABYCgKMAFwGAAAAYAoABACECgAAABgWJhwECFwGAXxISAMgdAgITALKHAQIXAYAAABIA2nUDAhMA2YcBAhIA23UDAhMA2ocBAhYBgAAAFgKAZwAXAYAAABgCgAEAIQKAAAAGBdaHAQIXAYB7EBIAyR0:
CAAAAElUSW5wK2hjU3dmUDJDNXJ2VEF5eWdpL2pxQmlMS1RPL29qM3pDNXEwcyt0eXJudDBUa2FrLzhoM0llVm5tdVAvaXNUK3hyOHdhblpMdVN6Y2dKTFNnPT3/AAAAAhcBgDcSEgDHHQICEwBlhwECFwGAAAASANp1AwITAIyHAQISANt1AwITAI2HAQIWAYAAABYCgKMAFwGAAAAYAoABACECgAAABgWJhwECFwGAXxISAMgdAgITALKHAQIXAYAAABIA2nUDAhMA2YcBAhIA23UDAhMA2ocBAhYBgAAAFgKAZwAXAYAAABgCgAEAIQKAAAAGBdaHAQIXAYB7EBIAyR0:
```

Response:
```
UwAAAGF1dGhvcml0eT1DcmFja2VyRm91ci9zZXJpYWw9NTU1MDAzMS9ob2xkZXI9QWVsaXRhL3R5cGU9c2lsdmVy/w==
UwAAAGF1dGhvcml0eT1DcmFja2VyRm91ci9zZXJpYWw9NDkyNzk5MS9ob2xkZXI9QWVsaXRhL3R5cGU9c2lsdmVy/w==
```

### Map travel

Request:

```
AfAR1Y0xCQk: 
```

Response (CC3):

```
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
```





