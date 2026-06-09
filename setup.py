from setuptools import setup, find_packages

setup(
    name="policy_bazar",
    version="0.1.0",
    description="ERPNext v15+ app: Policy Bazar insurance management with AI-based risk scoring",
    author="Your Name",
    author_email="you@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["openai>=1.0.0"],
    license="MIT",
    zip_safe=False,
    python_requires=">=3.10",
)
