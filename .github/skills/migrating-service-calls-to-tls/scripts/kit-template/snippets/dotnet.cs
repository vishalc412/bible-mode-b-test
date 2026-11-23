// .NET 8: calling {{PRODUCER}} with your client certificate, trusting only the producer's CA.
using System.Net.Http;
using System.Security.Cryptography.X509Certificates;

var clientCert = X509Certificate2.CreateFromPemFile(
    "/etc/tls/{{PRODUCER}}/client.crt", "/etc/tls/{{PRODUCER}}/client.key");
// A certificate-only file: the constructor reads PEM. (CreateFromPemFile is for a certificate WITH its key,
// and throws for a CA file. On .NET 9 and later use X509CertificateLoader.LoadCertificateFromFile.)
var producerCa = new X509Certificate2("/etc/tls/{{PRODUCER}}/ca-bundle.pem");

var handler = new SocketsHttpHandler();
handler.SslOptions.ClientCertificates = new X509CertificateCollection { clientCert };
handler.SslOptions.CertificateChainPolicy = new X509ChainPolicy
{
    TrustMode = X509ChainTrustMode.CustomRootTrust,   // only the producer's CA, not the machine store
    CustomTrustStore = { producerCa },
    RevocationMode = X509RevocationMode.NoCheck,
};
// Never add a callback that returns true.
// On Windows, a key loaded from PEM may need: clientCert = new X509Certificate2(clientCert.Export(X509ContentType.Pfx));

using var http = new HttpClient(handler);
var response = await http.GetAsync("{{ENDPOINT}}");
Console.WriteLine((int)response.StatusCode);
