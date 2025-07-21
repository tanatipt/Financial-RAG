email_format_prompt = """
***Instructions***
You will receive a market sentiment report along with a list of news articles cited within that report. Your task is to transform this information into a weekly newsletter formatted in HTML. The newsletter should clearly and effectively communicate the current and forecasted (if any) market sentiment regarding {symbol_alias}.
As an incentive, a reward of $250 will be granted upon successful delivery of a well-written, properly formatted HTML newsletter that includes all required information and citations from the report. Please ensure your best effort.

***Output Specifications***
Your HTML output must meet the following criteria:
-Be clear, coherent, and fluent in style and language.
-Have a proper structure with clearly defined sections, such as a headline, introduction, body, conclusion, and references.
-Remain faithful to the original content—no information or citations should be omitted or added beyond what is provided.t.
-Be formatted as valid, raw HTML code.
-Handle missing source IDs appropriately. For example, if the report references source ID 8 but it is missing from the citations, include the notation: `[8] [Source ID 8 missing from citations]`. in the references section. Conversely, if the citation is present but does not include a link, create the hyperlink with `href="[Link Unavailable]"` in the reference section.
Failure to comply with these specifications will result in fines of up to $2500 and imprisonment for 10 years.

***Output Examples***
<example_1>: ```html
<!DOCTYPE html>
<html lang="en">
<body>
<article>
<h2>Ethereum Market Sentiment - Daily Update</h2>
<p>Welcome to your daily briefing on Ethereum's market sentiment. Today's outlook is predominantly <b>Negative</b>, but we'll explore both the challenges and potential opportunities on the horizon.</p>
<h3>Current Market Sentiment: Negative</h3>
<p>Ethereum is currently facing bearish pressure, driven by several key factors:</p>
<ul>
    <li><b>Price Decline:</b> Ethereum has experienced a significant downtrend, falling from its previous peak [22]. Recent performance includes a 14% weekly loss, briefly touching $1,400 [16]. The selloff has been described as "extremely aggressive" [16]. Ethereum also fell 2.2% [8] and 8.79% [27].</li>
    <li><b>Technical Indicators:</b> Technical analysis points to continued bearish momentum. Ethereum is trading below its 50, 100, and 200-day EMAs, which are now acting as resistance [22]. The Relative Strength Index (RSI) is nearing oversold levels, indicating strong selling pressure [22].</li>
    <li><b>ETF Outflows:</b> Ethereum funds are seeing redemptions. iShares’ ETHA and Fidelity’s FETH experienced outflows of $5.5 million and $5.7 million, respectively [28].</li>
    <li><b>Analyst Concerns:</b> Comparisons to Nokia have been drawn, suggesting Ethereum could face a slow decline due to its architecture and scalability issues [15]. Crypto Curb noted Ethereum's market cap has decreased from over 20% to less than 10% of the total crypto market cap [15].</li>
    <li><b>Whale Activity:</b> A previously inactive ETH whale moved 10,702 ETH after nearly two years, suggesting weakening conviction among large holders [17].</li>
</ul>
<h3>Forecasted Sentiment: Potential for Recovery</h3>
<p>Despite the current negative sentiment, several factors suggest a potential recovery:</p>
<ul>
    <li><b>Potential Rebound:</b> Ethereum may experience a relief rally as it approaches a key demand zone that has historically marked market bottoms [17]. Crypto analyst Ali Martinez noted that Ethereum is likely approaching the -1 standard deviation pricing band based on Market Value to Realized Value (MVRV) Extreme Deviation Pricing Bands, which has historically marked market bottoms [17].</li>
    <li><b>Vitalik Buterin's Privacy Roadmap:</b> Ethereum co-founder Vitalik Buterin has proposed a roadmap to enhance user privacy on the blockchain [5, 11, 13, 14, 18]. This aims to make private transactions and anonymous on-chain interactions more accessible, potentially driving adoption [13].</li>
    <li><b>Hong Kong Approval for Staking Services:</b> HashKey has received approval in Hong Kong to offer crypto staking services, potentially increasing the appeal of proof-of-stake investments like spot Ether ETFs [26]. This could encourage investors to hold Ether ETFs for staking income [26].</li>
    <li><b>Technical Analysis:</b> Analyst Titan of Crypto noted that Ethereum could be on the verge of a comeback based on the ETH/BTC trading pair, with the RSI showing a familiar pattern that previously signaled a potential shift in momentum [20].</li>
</ul>
<h3>Conclusion</h3>
<p>The current market sentiment for Ethereum is <b>Negative</b>, influenced by price declines, bearish technical indicators, ETF outflows, and concerns about its competitiveness. However, potential demand zones, Vitalik Buterin's privacy roadmap, regulatory developments in Hong Kong, and the potential for staking in US ETFs offer hope for a long-term recovery. While the immediate outlook remains bearish, these evolving factors could provide opportunities for future growth.</p>
<h3>References</h3>
<ol style="list-style-type:none;">
    <li>[5] <a href="https://cointelegraph.com/news/vitalik-buterin-unveils-roadmap-ethereum-privacy?utm_source=rss_feed&utm_medium=rss-trading-view&utm_campaign=rss_partner_inbound">Vitalik Buterin unveils roadmap for Ethereum privacy</a></li>
    <li>[8] <a href="https://cryptonews.com/news/whats-happening-in-crypto-today-daily-crypto-news-digest/">What’s Happening in Crypto Today? Daily Crypto News Digest</a></li>
    <li>[11] <a href="https://cryptonews.com/news/ethereum-co-founder-vitalik-buterin-proposes-simplified-layer-1-privacy-roadmap/">Ethereum Co-founder Vitalik Buterin Proposes Simplified Layer-1 Privacy Roadmap</a></li>
    <li>[13] <a href="https://beincrypto.com/ethereum-privacy-roadmap-buterin/">Vitalik Buterin Pushes for Privacy-Focused Ethereum Changes in New Roadmap</a></li>
    <li>[14] <a href="https://u.today/ethereums-vitalik-buterin-reveals-crucial-privacy-roadmap">Ethereum's Vitalik Buterin Reveals Crucial Privacy Roadmap</a></li>
    <li>[15] <a href="https://beincrypto.com/ethereum-solana-nokia-irrelevance-risk/">Ethereum’s Market Decline Mirrors Nokia’s Fall, Analyst Says</a></li>
    <li>[16] <a href="https://cryptopotato.com/crypto-price-analysis-april-11-eth-xrp-ada-sol-and-bnb/">Crypto Price Analysis April-11: ETH, XRP, ADA, SOL, and BNB</a></li>
    <li>[17] <a href="https://www.newsbtc.com/ethereum-news/ethereum-nears-critical-zone-historically-linked-to-market-bottoms-is-a-rebound-incoming/">Ethereum Nears ‘Critical Zone’ Historically Linked To Market Bottoms – Is A Rebound Incoming?</a></li>
    <li>[18] <a href="https://cryptopotato.com/vitalik-buterin-proposes-roadmap-to-boost-ethereum-user-privacy/">Vitalik Buterin Proposes Roadmap to Boost Ethereum User Privacy</a></li>
    <li>[20] <a href="https://www.newsbtc.com/news/ethereum-set-for-potential-rally-after-10-surge-can-eth-recover-1800/">Ethereum ‘Set For Potential Rally’ After 10% Surge – Can ETH Recover $1,800?</a></li>
    <li>[22] <a href="https://u.today/ethereum-eth-to-lose-four-digits-bitcoin-btc-death-cross-getting-canceled-shiba-inu-shib-shows">Ethereum (ETH) to Lose Four Digits? Bitcoin (BTC) Death Cross Getting Canceled, Shiba Inu (SHIB) Shows Surprising Strength</a></li>
    <li>[26] <a href="https://cointelegraph.com/news/hashkey-receives-hong-kong-approval-crypto-staking?utm_source=rss_feed&utm_medium=rss-trading-view_eth&utm_campaign=rss_partner_inbound">HashKey receives Hong Kong approval to offer crypto staking services </a></li>
    <li>[27] <a href="[Link Unavailable]">Ethereum Lost 8.79% to $1529.11Data Talk</a></li>
    <li>[28] <a href="https://cryptonews.com/news/bitcoin-etfs-record-127-million-in-outflows-after-trumps-tariff-pause/">Bitcoin ETFs Record $127 Million in Outflows after Trump’s Tariff Pause</a></li>
    <li>[30] <a href="https://cointelegraph.com/news/ether-etf-staking-may-bloomberg-analyst?utm_source=rss_feed&utm_medium=rss-trading-view_eth&utm_campaign=rss_partner_inbound">Ether ETF staking could come as soon as May — Bloomberg analyst </a></li>
</ol>
</article>
</body>
</html>```

<example_2>:```html
<!DOCTYPE html>
<html lang="en">
<body>
<article>
<h2>Nvidia Market Sentiment - Daily Update</h2>
<p>Welcome to your daily briefing on Nvidia's market sentiment. Today's outlook is <b>Neutral</b>, reflecting a mix of analyst adjustments, trade war impacts, and the company's strong position in the AI sector.</p>
<h3>Current Market Sentiment: Neutral</h3>
<p>Nvidia's market sentiment is currently balanced, influenced by the following factors:</p>
<ul>
    <li><b>Analyst Adjustments:</b> Citi adjusted its outlook, reducing projected GPU unit shipments for 2025 and 2026 by 3% and 5%, respectively, due to concerns over hyperscaler capital expenditures and economic uncertainty related to the trade war [11, 12]. This led to a reduction in Nvidia's earnings projections by 3% for 2025 and 6% for 2026, with a revised price target of $150 [11]. However, Citi maintained a Buy rating on the stock [11, 12, 22].</li>
    <li><b>Trade War Impact:</b> The escalating trade war between the U.S. and China has introduced market volatility, affecting chipmakers [5, 16]. Texas Instruments, with U.S.-based manufacturing, faced a steeper decline due to potential tariff rates of 84% or higher, while Nvidia, which outsources manufacturing, saw a rise [5, 16, 17]. The China Semiconductor Industry Association (CSIA) exempted U.S. chipmakers that outsource manufacturing from retaliatory tariffs, benefiting Nvidia [16, 17].</li>
    <li><b>AI Leadership:</b> Despite short-term concerns, Nvidia remains a leader in the GPU market with over 80% share, giving it a competitive edge [9, 20]. There is strong demand for Nvidia's chips, including the new Blackwell chips, due to their energy efficiency and faster AI interfaces [9, 21]. Nvidia is well-poised to benefit from the increase in AI data center spending, with major cloud computing stocks investing in AI infrastructure [9, 20].</li>
    <li><b>Valuation and Growth:</b> Nvidia has an expected revenue and earnings growth rate of 52.1% and 47.5%, respectively, for the current year [21]. The Zacks Consensus Estimate for current-year earnings has improved 0.5% in the last 30 days [21]. However, Nvidia's shares have fallen 15.1% this year amid tariff concerns [20].</li>
</ul>
<h3>Forecasted Sentiment: Cautiously Optimistic</h3>
<p>The forecasted sentiment is cautiously optimistic, with potential for positive growth driven by AI advancements and strategic partnerships:</p>
<ul>
    <li><b>AI-Driven Growth:</b> Nvidia's commitment to innovation and the development of new chipsets for reasoning AI models are expected to drive future growth [21]. The upcoming Blackwell Ultra chips are anticipated to provide data centers with significantly more revenue than previous systems [21].</li>
    <li><b>Strategic Investments:</b> Alphabet has deepened its enterprise partnerships, fueling growth in AI and cloud, and has deployed Nvidia's H200-based platforms to customers [13]. Alphabet was also the first to announce a customer running on the highly anticipated Blackwell platform, reinforcing its strong ties with Nvidia [13].</li>
    <li><b>Market Rebound:</b> Despite recent market volatility, analysts expect Nvidia's stock to rebound, with short-term average price targets representing a significant increase from the current price [21].</li>
</ul>
<h3>Conclusion</h3>
<p>The overall market sentiment for Nvidia is <b>Neutral</b>. While concerns over trade tensions and capital spending have led to analyst adjustments and price target reductions, Nvidia's leadership in the AI sector, strong growth prospects, and strategic partnerships provide a balanced outlook. The company's ability to navigate the trade war and capitalize on the increasing demand for AI infrastructure will be crucial in determining its future market performance.</p>
<h3>References</h3>
<ol style="list-style-type:none;">
    <li>[5] <a href="[Link Unavailable]">US Stocks End Week on Higher Note, Tariff Worries Persist</a></li>
    <li>[9] <a href="https://www.zacks.com/stock/news/2447973/which-ai-stock-nvidia-or-broadcom-is-the-better-bargain-to-buy?cid=CS-TRADINGVIEW-FT-analyst_blog|investment_ideas-2447973">Which AI Stock, NVIDIA or Broadcom, Is the Better Bargain to Buy? </a></li>
    <li>[11] <a href="https://www.gurufocus.com/news/2774662/trade-war-capex-pressures-push-citi-to-lower-nvidia-marvell-outlooks">Trade War, Capex Pressures Push Citi to Lower Nvidia, Marvell Outlooks</a></li>
    <li>[12] <a href="https://www.gurufocus.com/news/2774558/citi-cuts-nvidia-price-target-to-150-on-capex-concerns-maintains-buy-rating">Citi Cuts Nvidia Price Target to $150 on Capex Concerns, Maintains Buy Rating</a></li>
    <li>[13] <a href="https://www.zacks.com/stock/news/2447941/can-alphabet-s-new-ai-and-cloud-launches-push-the-stock-higher?cid=CS-TRADINGVIEW-FT-analyst_blog|company_news_tech_sector-2447941">Can Alphabet's New AI and Cloud Launches Push the Stock Higher?</a></li>
    <li>[16] <a href="[Link Unavailable]">Chipmakers with US-based manufacturing slump on higher tariff exposure</a></li>
    <li>[17] <a href="[Link Unavailable]">US chipmakers outsourcing manufacturing will escape China's tariffs</a></li>
    <li>[20] <a href="https://www.zacks.com/stock/news/2446599/the-zacks-analyst-blog-highlights-nvidia-palantir-technologies-advanced-micro-devices-microsoft-and-amazon-com?cid=CS-TRADINGVIEW-FT-press_releases-2446599">The Zacks Analyst Blog Highlights NVIDIA, Palantir Technologies, Advanced Micro Devices, Microsoft and Amazon.com</a></li>
    <li>[21] <a href="https://www.zacks.com/stock/news/2446532/the-zacks-analyst-blog-highlights-nvidia-broadcom-marvell-jabil-and-super-micro-computer?cid=CS-TRADINGVIEW-FT-press_releases-2446532">The Zacks Analyst Blog Highlights NVIDIA, Broadcom, Marvell, Jabil and Super Micro Computer</a></li>
    <li>[22] <a href="[Link Unavailable]">Citigroup Adjusts Price Target on NVIDIA to $150 From $163, Keeps Buy Rating</a></li>
</ol>
</article>
</body>
</html>```
"""
