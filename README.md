
<br>
  <table style="border: 1px solid transparent">    
    <tr>
      <td>
  <a href="http://talky.readthedocs.io"><img src="https://img.shields.io/badge/Wiki-%23000000.svg?style=for-the-badge&logo=wikipedia&logoColor=white"></a>
  <a href="https://github.com/mraniki/tt/"><img src="https://img.shields.io/badge/github-%23000000.svg?style=for-the-badge&logo=github&logoColor=white"></a><br>
  <a href="https://hub.docker.com/r/mraniki/tt"><img src="https://img.shields.io/docker/pulls/mraniki/tt?style=for-the-badge"></a>
  <br>
      </td>
      <td align="center"><img width="200" alt="Logo" src="https://github.com/mraniki/cefi/blob/main/docs/_static/logo-full.png"></td>
    </tr>
    <tr>
      <td>
        <a href="https://pypi.org/project/cefi/"><img src="https://img.shields.io/pypi/v/cefi?style=for-the-badge&logo=PyPI&logoColor=white"></a><br>
        <a href="https://pypi.org/project/cefi/"><img src="https://img.shields.io/pypi/dm/cefi?style=for-the-badge&logo=PyPI&logoColor=white&label=pypi&labelColor=grey"></a><br>
        <a href="https://github.com/mraniki/cefi/"><img src="https://img.shields.io/github/actions/workflow/status/mraniki/cefi/%F0%9F%91%B7Flow.yml?style=for-the-badge&logo=GitHub&logoColor=white"></a><br>
    <a href="https://talky.readthedocs.io/"><img src="https://readthedocs.org/projects/cex/badge/?version=latest&style=for-the-badge"></a><br>
    <a href="https://codebeat.co/projects/github-com-mraniki-cefi-main"><img src="https://codebeat.co/badges/6aecf822-ea11-499c-80d9-37cd3f35b923"/></a><br>
    <a href="https://app.codacy.com/gh/mraniki/cefi/dashboard"><img src="https://app.codacy.com/project/badge/Grade/2e375e4df911416980496bfd568f0d76"/></a><br>
    <a href="https://codecov.io/gh/mraniki/cefi"> <img src="https://codecov.io/gh/mraniki/cefi/branch/main/graph/badge.svg?token=BTIoKrcXNq"/></a><br>
      </td>
      <td align="left"> 
        Interact with centralized trading platforms (CEX)<br>
        supported by CCXT, Capital.com, DEGIRO, IBKR and others.
      </td>
    </tr>
  </table>

  <h5>How to use it</h5>
  <pre>
  <code>


    cex = CexTrader()

    balance = await cex.get_balances()
    print("balance ", balance)

    symbol = "BTC"
    quote = await cex.get_quotes(symbol)
    print("quote ", quote)

    order = {
        "action": "BUY",
        "instrument": "BTC",
        "quantity": 1,
    }
    order = await cex.submit_order(order)
    print("order ", order)

  </code>
  </pre>
  <h5>Documentation</h5>
  <a href="https://talky.readthedocs.io/projects/cefi/en/latest/"><img src="https://img.shields.io/badge/Documentation-000000?style=for-the-badge&logo=readthedocs&logoColor=white"></a><br>
