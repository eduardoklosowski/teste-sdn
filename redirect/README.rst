Subir Rede
==========

.. code-block:: sh

  mn --topo single,3 --mac --switch ovsk --controller remote,192.168.122.1


Subir Controller sem Redirect
=============================

.. code-block:: sh

  ryu-manager --verbose l2switch.py base.py


Subir Controller com Redirect
=============================

Redireciona os pacotes HTTP (TCP 80) do servidor ``10.0.0.2`` para o servidor ``10.0.0.3``.

.. code-block:: sh

  ryu-manager --verbose redirecttcp.py l2switch.py base.py


Controlar via API REST
======================

- Para verificar o estado do redirect, acesse: http://127.0.0.1:8080/redirecttcp
- Para ativar/desativar o redirect, acesse: http://127.0.0.1:8080/redirecttcp/change


Teste
=====

**h2** e **h3**:

.. code-block:: sh

  # Servidor HTTP
  python3 -m http.server 80

  # Servidor RTP
  gst-launch-1.0 -v videotestsrc ! videoconvert ! vp8enc ! rtpvp8pay ! tcpserversink host=0.0.0.0 port=80

**h1**:

.. code-block:: sh

  # Cliente HTTP
  wget -O- 10.0.0.2

  # Cliente RTP
  gst-launch-1.0 -v tcpclientsrc host=10.0.0.2 port=80 ! application/x-rtp, encoding-name="(string)VP8" ! rtpvp8depay ! vp8dec ! autovideosink
