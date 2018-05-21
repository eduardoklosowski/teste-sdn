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


Teste
=====

**h2** e **h3**:

.. code-block:: sh

  python3 -m http.server 80

**h1**:

.. code-block:: sh

  wget -O- 10.0.0.2
