
  

## Simplest, Cleanest and Efficient Python Library to Scrape Stocks, FnO & Indices Data From The NSEIndia(New) and NiftyIndices Website.

  

`nsemine` is a Python library designed to provide a clean and straightforward interface for scraping data from the National Stock Exchange of India (NSE) and the Nifty Indices website. It aims to simplify the process of retrieving various market data, including indices, stock information, futures & options data, and general NSE-related utilities. This library is built to be efficient and user-friendly, catering to **developers**, **traders**, **investors** who need reliable NSE data for financial analysis, algorithmic trading, and data visualization.

  
  

## Features

  

*  **Asynchronous Data Retrieval:**  &nbsp;Experience non-blocking, asynchronous data retrieval for optimal performance. Leverage the power of `asyncio` to fetch market data without delays, ensuring your applications remain responsive.

  

*  **High-Speed Data Acquisition:**  &nbsp;Utilize the speed and efficiency of `aiohttp` and `requests` under the hood. This library is designed for rapid data acquisition, enabling you to get the latest market insights quickly.

  * **Unparalleled Data Flexibility:** &nbsp; `nsemine` empowers you with the complete data manipulation. Choose between the raw, unfiltered API response for maximum customization, OR leverage our intelligently processed data structures for streamlined analysis and immediate insights.

*  **Intelligent Built-in Caching:**  &nbsp;Minimize API requests with the intelligent built-in caching mechanism. Reduce your reliance on the NSE API and save you from getting blocked by the NSE Anti-Scraper Robots.

  

*  **Clean and Intuitive API:**  &nbsp;Designed for simplicity and ease of use, the library provides a clean and intuitive API, allowing developers to quickly integrate NSE data into their projects.

  

*  **Comprehensive Data Coverage:**  &nbsp;Access a wide range of NSE data, including indices, stocks, futures, and options, all within a single, unified library.

  

*  **Robust Error Handling:**  &nbsp;Built with robust error handling to ensure your applications remain stable and resilient, even in challenging network conditions.

  

  

## Installation

  

You can install `nsemine` by pip or via github.

  

>  ``pip install nsemine``

  

OR

  

>``pip install git+https://github.com/kbizme/nsemine.git``

  

## Why I Built This Library

  

Well, there are several Python libraries available for scraping NSE data, I developed this library to address specific needs that were not adequately met by the existing solutions. I have used this library in my project. You can use it in yours.

  

*  **Custom Data Requirements:**  &nbsp;&nbsp;``nsemine`` is tailored to retrieve specific data points and formats that were essential for the project, which may not be available in other libraries.

  

  

*  **Unique Data Structures:** The project required data in a particular structure and format, which this library delivers directly, eliminating the need for extensive post-processing.

  

  

*  **Data Availability:**&nbsp;&nbsp;  ``nsemine`` is designed to access and provide data that may not be available or easily accessible through other existing NSE scraping libraries.

  

  

*  **Performance and Reliability:** Optimized for speed and stability, ensuring reliable data retrieval, especially for real-time and high-frequency data. It uses ``numpy`` and ``pandas`` vectorized operations for faster data pre-processing. Most of the possible errors are handled with Exceptions, thus, even if any error occurs the application will remain stable.

  

  

*  **Ease of Use:**  &nbsp;&nbsp;``nsemine`` aims to provide a simple and intuitive interface, making it easy for developers to integrate NSE data into their applications. This library is designed to offer a more specialized and efficient solution for users who require precise and customized NSE data.

  

  

## Contributing

  

Contributions are welcome! Please feel free to submit pull requests or open issues for bug fixes, feature requests, or improvements.

  

## Documentation

  

_Work in progress..._ Meanwhile, you may explore the library. ReadTheDocs style documentation will be added upon complete library build.