# Internal server for the Sarathi container. TLS is handled by the shared proxy.
{
	auto_https off
	admin off
}

:80 {
	root * /srv
	encode zstd gzip

	@assets path /assets/* /data/* /audio/* /chant/*
	header @assets Cache-Control "public, max-age=604800"
	header ?Cache-Control "public, max-age=3600"
	header {
		X-Content-Type-Options nosniff
		Referrer-Policy strict-origin-when-cross-origin
		-Server
	}

	file_server

	handle_errors {
		@404 expression {err.status_code} == 404
		handle @404 {
			rewrite * /404.html
			file_server
		}
	}
}
