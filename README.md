<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->
<div align="center">

[![Python][python-shield]][python-url]
[![Stargazers][stars-shield]][stars-url]
[![Workflow][workflow-shield]][workflow-url]
[![License][license-shield]][license-url]

</div>

<!-- PROJECT LOGO -->
<br />
<div align="center">

<a href="https://github.com/chuamatt/internship-portal">
    <img src="https://i.imgur.com/HQtRKSV.png" alt="screenshot" height="350">
  </a>

  <h3 align="center">Internship Portal Scraper</h3>

  <p align="center">
    Because SP's internship portal is a pain to use<br>and is just calling out to be scraped.
  </p>
</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#why">Why?</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#support">Support</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- WHY -->
## Why?

SP's internship portal is buggy. Like, really buggy. 

I'm not sure how much INP paid for this, but it's not worth it. Features look meh, it's slow, and it's a right pain in the a**.

Being intrigued at just how shitty the internship portal is, a few friends and I decided to explore the website. We found that the API calls it made returned way more information than what was being shown on the frontend website. It's also easy to scrape the internship portal as there's no ratelimit imposed (in part because the portal itself makes like a bazillion requests). 

I did try to make a web-based project to replace the internship portal, but I couldn't get it to work because it [unfortunately isn't allowed to set a cross-origin header for requests with Cookie](https://developer.mozilla.org/en-US/docs/Glossary/Forbidden_header_name). Granted, there definitely are security concerns behind doing this, but errrghhhhhh. Without an authorisation cookie, I can't make requests to the internship portal. Thus, python it is.

The difficult part of this project was trying to outdo the internship portal's shitty UI. I'm not sure if I succeeded, but I tried my best. One aspect was the portal's "estimated commute time" feature, which doesn't even work. In this case, I implemented a variant using distances from MRT stations instead, with the coordinates found using the public OneMap API. 

This script makes requests to the internship portal to find out which students got an internship, then lists these details in an embed, which is then sent to a Discord channel. 

Being interested in CICD, I also decided to implement a GitHub Actions workflow to run the script, with the user manually inputting the IntsPortal Auth Cookie. I learnt the basic syntax of workflows, trigger options and how to use secrets (the first few times, oops, secrets were openly exposed -- I had to regenerate them before making this repo public).

Given the lack of proper authentication and access controls, it is also possible to modify this script to get the internship details of the entire school by simply iterating over the job ids, then export these details to a file. This is definitely a security breach though, so I'm not going to do it.


<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

These are the instructions on setting up your project locally.

### Support

If you choose to clone this to run on your own machine, please note that only best-effort support is provided. Should you need assistance, please open an issue with the tag `help wanted` and I will do my best to help you.

If you do not have a IntsPortal Auth Cookie, this script **will not work** for you. Please **do not** open an issue to ask for a auth cookie.

### Installation

This project is built to work with Github Actions, and not on your local machine. Thus, you'd need to make some changed so the script can work on your machine.

1.  Clone the repo
    ```sh
    git clone https://github.com/chuamatt/internship-portal.git
    ```
2.  Install external dependencies from pip
    ```sh
    pip install -r requirements.txt
    ```
   3.  Modify `webhook.py` such that your own IntsPortal Auth Cookie is in `headers["cookie"]`, and your Discord Webhook URL is in `WEBHOOK_URL`
       ```py
       headers = CaseInsensitiveDict()
       # headers["cookie"] = os.environ.get("COOKIE")
       headers["cookie"] = "YOUR INTSPORTAL AUTH COOKIE HERE"
       ```
       ```py
       # WEBHOOK_ID = os.environ.get("WEBHOOK_ID")
       # WEBHOOK_TOKEN = os.environ.get("WEBHOOK_TOKEN")
       # WEBHOOK_URL = f"https://discord.com/api/webhooks/{WEBHOOK_ID}/{WEBHOOK_TOKEN}"
       WEBHOOK_URL = "YOUR DISCORD WEBHOOK URL HERE"
       ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

 Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork this repo and create a pull request. You can also simply open an issue with the tag `enhancement`.
Don't forget to give the project a star⭐! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the AGPL-3.0 License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Thank you to the great people on the Internet helping one another! I've included a few of the resources that helped me in this project below.

* [Stack Overflow](https://stackoverflow.com)
* [Img Shields](https://shields.io)
* [HDB Resale API](https://github.com/yuan-yexi/hdb-resale-api/blob/master/script.py)
* [Best README Template](https://github.com/othneildrew/Best-README-Template)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[python-shield]: https://img.shields.io/badge/python%203.9-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[python-url]: https://www.python.org/downloads/release/python-3916/
[stars-shield]: https://img.shields.io/github/stars/chuamatt/internship-portal.svg?style=for-the-badge
[stars-url]: https://github.com/chuamatt/internship-portal/stargazers
[workflow-shield]: https://img.shields.io/github/actions/workflow/status/chuamatt/internship-portal/main.yml?branch=main&style=for-the-badge
[workflow-url]: https://github.com/chuamatt/internship-portal/actions
[license-shield]: https://img.shields.io/github/license/chuamatt/internship-portal.svg?style=for-the-badge
[license-url]: https://github.com/chuamatt/internship-portal/blob/master/LICENSE.txt