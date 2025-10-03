from google import genai
from google.genai import types

import asyncio


class GeminiChat:
    __model_name: str = "gemini-2.5-pro"

    def __init__(self, api_key: str, prompt: str):
        self.prompt = prompt
        self.api_key = api_key

        if not self.api_key:
            raise EnvironmentError("GEMINI_KEY environment variable not set")

    async def send_request(self):
        client = genai.Client(
            api_key=self.api_key
        ).aio
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )
        response = await client.models.generate_content(
            model=self.__model_name,
            contents=self.prompt,
            config=config,
        )
        return response.text


async def main():
    list_of_qualities = [
                {
                "name": "Tozero Solutions",
                "website": "https://www.tozero.solutions/",
                "qualities": {
                    "mission": "To establish a sustainable and circular economy for lithium-ion batteries.",
                    "vision": "To create a future where battery waste is eliminated through innovative recycling processes.",
                    "values": [
                    "Sustainability",
                    "Innovation",
                    "Circular Economy",
                    "Environmental Responsibility"
                    ],
                    "technologies": [
                    "Advanced hydrometallurgical recycling process for lithium-ion batteries."
                    ],
                    "innovation": "Developing a more energy-efficient and cost-effective method for recovering critical materials from batteries, such as lithium, cobalt, and nickel.",
                    "principles": "A focus on creating a closed-loop system for battery materials to reduce reliance on mining and minimize environmental impact."
                }
                },
                {
                "name": "Reverion",
                "website": "https://reverion.com/",
                "qualities": {
                    "mission": "To enable climate-positive power generation at scale with existing renewable resources.",
                    "vision": "To pave the way to 100 percent renewable energy by harnessing the full potential of biogas.",
                    "values": [
                    "Sustainability",
                    "Innovation",
                    "Efficiency",
                    "Climate Action"
                    ],
                    "technologies": [
                    "Reversible, high-temperature fuel cell systems that can generate electricity from biogas and also produce green hydrogen or synthetic natural gas.",
                    "Carbon capture technology to enable negative CO2 emissions."
                    ],
                    "innovation": "Development of an all-in-one power plant solution that is highly efficient, reversible, and capable of carbon capture, making it a key technology for the energy transition.",
                    "principles": "A commitment to providing scalable and readily available solutions to combat the climate crisis and ensure a reliable, clean energy future."
                }
                },
                {
                "name": "Silc",
                "website": "https://www.silc.com/",
                "qualities": {
                    "mission": "To make a meaningful contribution to the growth and prosperity of our communities and stakeholders.",
                    "vision": "To be the most highly regarded and preferred alternative assets investment platform in the world.",
                    "values": [
                    "Sustainability",
                    "Integrity",
                    "Leadership",
                    "Collaboration"
                    ],
                    "technologies": [
                    "A turnkey digital platform for investment managers and asset sponsors to connect with wholesale investors."
                    ],
                    "innovation": "Providing specialized and alternative investment opportunities and solutions that are otherwise unattainable for wholesale clients.",
                    "principles": "A focus on being specialists in alternative assets, offering enhanced choice, convenience, and a differentiated value proposition for their clients. Their culture is characterized as being different, leading-edge, high-functioning, collaborative, and entrepreneurial."
                }
                },
                {
                "name": "nT-Tao Compact Fusion Power",
                "website": "https://www.nt-tao.com/",
                "qualities": {
                    "mission": "To develop a unique nuclear fusion technology that will enable the world to transition toward a cleaner, decarbonized, sustainable, and democratized future.",
                    "vision": "To accelerate the path to commercial nuclear fusion with a compact and scalable system.",
                    "values": [
                    "Innovation",
                    "Sustainability",
                    "Scalability",
                    "Energy Independence"
                    ],
                    "technologies": [
                    "Compact fusion reactor technology utilizing a proprietary plasma heating method and an innovative magnetic chamber topology to achieve high plasma densities."
                    ],
                    "innovation": "Developing a highly scalable, container-sized fusion reactor that is significantly smaller, more cost-effective, and quicker to deploy than traditional fusion projects. [18, 24]",
                    "principles": "A commitment to creating a clean, safe, and abundant energy source that can be deployed in a distributed manner, empowering industries and communities globally."
                }
                },
                {
                "name": "Ineratec",
                "website": "https://www.ineratec.de/en",
                "qualities": {
                    "mission": "To replace crude oil and achieve a carbon-neutral climate.",
                    "vision": "To shape the future of energy with sustainable e-fuels and chemicals.",
                    "values": [
                    "Sustainability",
                    "Innovation",
                    "Technological Expertise",
                    "Entrepreneurial Drive"
                    ],
                    "technologies": [
                    "Modular chemical plants for Power-to-X and Gas-to-X applications, converting renewable hydrogen and CO2 into e-kerosene, CO2-neutral diesel, synthetic waxes, and methanol."
                    ],
                    "innovation": "Pioneering the production of synthetic fuels and chemicals in compact, modular plants, making sustainable alternatives to fossil fuels more accessible and scalable.",
                    "principles": "A focus on defossilization through the creation of e-fuels and e-waxes, contributing to climate-neutral mobility and a sustainable future."
                }
                },
                {
                "name": "Seurat",
                "website": "https://www.seurat.com/",
                "qualities": {
                    "mission": "To delight consumers by embracing and celebrating diversity in thought and perspective.",
                    "vision": "To enable customers to reimagine what is possible at scale, unlocking future potential for their products and business.",
                    "values": [
                    "Challenging the status quo",
                    "Optimism",
                    "Realism",
                    "Engagement and Teamwork",
                    "Can-Do Attitude",
                    "Drive for Results",
                    "Inclusive Mindset",
                    "Collaboration",
                    "Entrepreneurial Passion"
                    ],
                    "technologies": [
                    "Area Printing®, a proprietary metal additive manufacturing technology that uses a powerful laser with over 2.3 million pixels to weld thin metal powder layers."
                    ],
                    "innovation": "Area Printing® technology decouples resolution and speed, enabling high-volume, cost-effective, and high-quality 3D printing of metal parts that can compete with traditional manufacturing methods like casting and forging. [7, 30]",
                    "principles": "Transforming global manufacturing by building future-ready metal parts factories, creating a new manufacturing asset class, and enabling a more agile and green global supply chain."
                }
                },
                {
                "name": "Sono Charge Energy",
                "website": "https://www.sonochargeenergy.com/",
                "qualities": {
                    "mission": "Pioneering advanced technologies to make the world's batteries last longer, charge faster, and be safer.",
                    "vision": "To build a more efficient and eco-friendly world by improving battery performance.",
                    "values": [
                    "Excellence",
                    "Teamwork",
                    "Innovation",
                    "Integrity"
                    ],
                    "technologies": [
                    "Acoustic wave technology that uses sound waves to improve the electrolytic motion within lithium-ion batteries. [19, 25]"
                    ],
                    "innovation": "Developing a novel, cost-effective solution that extends battery life, enables faster charging, and enhances safety by reducing lithium plating and dendritic formation. [19, 25, 28]",
                    "principles": "A commitment to fostering a diverse and inclusive workplace and upholding robust Corporate Social Responsibility practices to make a positive impact on society and the planet."
                }
                },
                {
                "name": "Drivemode",
                "website": "https://www.drivemode.com/",
                "qualities": {
                    "mission": "To simplify technology for drivers and create a safer, more connected driving experience.",
                    "vision": "To be the leading provider of intuitive and safe in-car technology solutions.",
                    "values": [
                    "Safety",
                    "Simplicity",
                    "User Experience",
                    "Innovation"
                    ],
                    "technologies": [
                    "Mobile applications and connected car platforms that integrate with vehicle systems to provide a seamless and safe user experience."
                    ],
                    "innovation": "Developing user-friendly interfaces and voice-enabled controls that minimize driver distraction while providing access to essential apps and services.",
                    "principles": "A focus on human-centered design to create automotive technology that is both easy to use and enhances driver safety."
                }
                },
                {
                "name": "SoundHound AI",
                "website": "https://www.soundhound.com/",
                "qualities": {
                    "mission": "To voice-enable the world with conversational intelligence. [39]",
                    "vision": "To create a voice AI platform that exceeds human capabilities and brings value and delight via an ecosystem of billions of products enhanced by innovation and monetization opportunities. [39]",
                    "values": [
                    "Supportive of Each Other",
                    "Open, Honest, and Ethical, Even When Hard",
                    "Undaunted by Challenges and Obstacles",
                    "Nimble, Focused, Fast – and Always Learning",
                    "Determined to Excel and Win"
                    ],
                    "technologies": [
                    "Independent voice AI platform featuring Speech-to-Meaning® and Deep Meaning Understanding® technologies. [39]"
                    ],
                    "innovation": "Connecting people to brands through customized conversational experiences that voice-enable products, services, and apps, while giving companies control over their data and brand experience. [39]",
                    "principles": "A belief that every brand should have a voice and every person should be able to interact naturally with the products around them by talking. A commitment to ethical AI development, including data privacy, diversity, and accessibility. [44]"
                }
                },
                {
                "name": "SES AI",
                "website": "https://www.ses.ai/",
                "qualities": {
                    "mission": "To accelerate the world's energy transition through material discovery and battery management. [41]",
                    "vision": "To power a future where electric vehicles dominate the automotive market, providing a superior driving experience without compromising safety or environmental responsibility. [2]",
                    "values": [
                    "Innovation",
                    "Sustainability",
                    "Performance",
                    "Collaboration"
                    ],
                    "technologies": [
                    "High-performance Lithium-Metal (Li-Metal) rechargeable batteries, AI-enhanced for high energy density and safety. [2, 33]",
                    "Avatar, an AI for safety that predicts battery health, and Molecular Universe, an AI for science to accelerate material discovery. [27]"
                    ],
                    "innovation": "Developing the world's most advanced Li-Metal battery technology that combines the high energy density of Li-Metal with the large-scale manufacturability of conventional Lithium-ion batteries. [42]",
                    "principles": "A commitment to revolutionizing electric vehicle performance and safety, driving the transition to a cleaner and more sustainable transportation future, and setting new industry standards for battery technology. [2, 5]"
                }
                },
                {
                "name": "helm.ai",
                "website": "https://helm.ai/",
                "qualities": {
                    "mission": "To make scalable autonomous driving a reality by creating the most reliable self-driving AI software and partnering with global automakers to deploy it in mass production. [22]",
                    "vision": "To build the most reliable and scalable AI system for any vehicle.",
                    "values": [
                    "Safety",
                    "Reliability",
                    "Scalability",
                    "Collaboration"
                    ],
                    "technologies": [
                    "AI-first software for ADAS to Level 4 autonomous driving, built on Deep Teaching™, a form of unsupervised learning. [22, 26]",
                    "Generative AI DNN architectures for real-time deployment and scalable training. [26]"
                    ],
                    "innovation": "A unified approach to developing and validating AI software for high-end ADAS through L4 autonomous driving that reduces reliance on large-scale fleet data, traditional simulations, and human annotation, making the approach more scalable and cost-efficient. [4, 22]",
                    "principles": "A belief that the future of mobility is autonomous and a commitment to providing cutting-edge AI software that is safe, cost-effective, and feature-rich. Development aligns with key automotive safety and quality standards like ISO 26262 and ASPICE. [26]"
                }
                },
                {
                "name": "Emulsion Flow Technologies",
                "website": "https://emulsion-flow.tech/",
                "qualities": {
                    "mission": "To contribute to solving resource and environmental challenges worldwide through the dissemination of their technology.",
                    "vision": "To lead our limited rare metals to the future. [36, 38]",
                    "values": [
                    "Sustainability",
                    "Innovation",
                    "Social Contribution",
                    "Efficiency"
                    ],
                    "technologies": [
                    "Emulsion Flow, an innovative solvent extraction technology for recovering rare metals and removing pollutants. [29]"
                    ],
                    "innovation": "A revolutionary solvent extraction method that is more compact, continuous, and cleaner than conventional methods, enabling horizontal recycling where recovered rare metals can be directly reused in high-tech industries. [16, 32]",
                    "principles": "Harnessing advanced separation technologies originating from nuclear research to address global resource and environmental challenges, including the recycling of rare metals from lithium-ion batteries and the removal of environmental contaminants like PFAS."
                }
                },
                {
                "name": "Princeton Nuenergy",
                "website": "https://pnecycle.com/",
                "qualities": {
                    "mission": "To deliver a cost-efficient, environmentally friendly solution to the current industry pain points of high operational costs and low efficiency in battery recycling.",
                    "vision": "To redefine lithium-ion battery recycling and lead the charge towards a greener, more efficient future.",
                    "values": [
                    "Sustainability",
                    "Innovation",
                    "Cost-Effectiveness",
                    "Environmental Responsibility"
                    ],
                    "technologies": [
                    "Patented low-temperature plasma-assisted separation process (LPAS™) for direct recycling of lithium-ion batteries. [10, 11]"
                    ],
                    "innovation": "A direct recycling method that regenerates cathode and anode materials from spent batteries, significantly reducing energy consumption, water usage, and CO2 emissions compared to traditional recycling methods. [9, 11, 13]",
                    "principles": "A commitment to creating a circular economy for battery manufacturing and recycling by recovering high-purity materials suitable for reintroduction into the battery supply chain, thereby reducing reliance on foreign supply chains and supporting US national security. [13]"
                }
                }
            ]
    api_key = 'AIzaSyAHYQ3FNi3u_qfZvvg-xMQ9Saa44w5R7sM'
    prompt = f"""
    You are a meta-analysis research analyst. Your task is to extract the core qualities, values, technologies, innovation and principles of the following companies based on available informations online. Focus on identifying aspects related to their mission, vision, ethics, technologies, innovations and operational philosophy. Return a JSON object containing with keys 'name', 'website' and 'qualities' for each company.
        **** Name: Tozero Solutions | Website: https://www.tozero.solutions/
        **** Name: Reverion | Website: https://reverion.com/
        **** Name: Silc | Website: https://www.silc.com/
        **** Name: nT-Tao Compact Fusion Power | Website: https://www.nt-tao.com/
        **** Name: Ineratec | Website: https://www.ineratec.de/en
        **** Name: Seurat | Website: https://www.seurat.com/
        **** Name: Sono Charge Energy | Website: https://www.sonochargeenergy.com/
        **** Name: Drivemode | Website: https://www.drivemode.com/
        **** Name: SoundHound AI | Website: https://www.soundhound.com/
        **** Name: SES AI | Website: https://www.ses.ai/
        **** Name: helm.ai | Website: https://helm.ai/
        **** Name: Emulsion Flow Technologies | Website: https://emulsion-flow.tech/
        **** Name: Princeton Nuenergy | Website: https://pnecycle.com/
    """
    prompt2 = f"""
Based on the following list of core qualities for a company, what is the single, overarching essence or theme that defines its identity? Respond with only the essence string and nothing else for each company.

Qualities: {list_of_qualities}
"""
    prompt3 = f"""
Based on the following list of core essences from my ideal companies, synthesize a single, concise 'master essence' that captures the collective identity, values, and strategic focus of these companies. The master essence should be a phrase that can be used to evaluate other companies for alignment. Respond with only the master essence string and nothing else.

Essences: [
'Tozero Solutions: Sustainable lithium-ion battery circular economy',
'Reverion: Climate-positive energy generation from biogas',
'Silc: Democratizing alternative asset investments',
'nT-Tao Compact Fusion Power: Accelerating commercial fusion with compact, scalable reactors',
'Ineratec: Defossilization through modular Power-to-X technology',
'Seurat: High-volume, scalable metal additive manufacturing',
'Sono Charge Energy: Advanced battery performance through acoustic wave technology',
'Drivemode: Simplified and safer in-car user experience',
'SoundHound AI: Voice-enabling the world with conversational intelligence',
'SES AI: Revolutionizing EV batteries with AI-powered Lithium-Metal technology',
'helm.ai: Scalable AI software for autonomous driving',
'Emulsion Flow Technologies: Solving resource challenges with advanced rare metal recycling',
'Princeton Nuenergy: Cost-efficient, environmentally friendly direct battery recycling'
]


"""
    chat = GeminiChat(
        api_key=api_key,
        prompt=prompt3
    )

    resp = await chat.send_request()
    print(resp)
    return resp


if __name__ == "__main__":
    asyncio.run(main())
