# NotSoStrict

**This tool is for educational purposes only. Hacking/testing without express consent from the target applcation's owner is illegal even ethical hacking. The owner of this tool is not responsible for anything others do with this. Be good please**

NotSoStrict is a Man-in-the-Middle emulator for SSL Stripping testing. This tool allows the user to create a mock 'victim machine' utilizing namespaces on their machine while also allowing the user to perform a MitM attack between the emulated browser and public facing web apps. The MitM and SSL Stripping tool used in here is bettercap.

### How to Use NotSoStrict
1. Download and unzip the project to your system>
```
cd NotSoStrict
git clone https://github.com/0ber1n/NotSoStrict.git
cd NotSoStrict
chmod +x NotSoStrict.py Bettercap_Launch.sh
```
2. Launch the NotSoStrict.py elevated.
```
sudo ./NotSoStrict.git
```
3. You will notice a Chromium browser will open up as well as a second terminal that launches the Bettercap portion.
4. In the Betteracap terminal, enter a filename for the pcap you want to create.
5. In the chromium browser, navigate to any site that allows an HTTP connection (The goal here is to look for missing HSTS headers, or at least preload).
6. When you get the evidence needed, exit the script by hitting ctrl + C.
7. Upload the pcap file created in the directory into WireShark and look for HTTP Streams with the data you need.
