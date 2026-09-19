# Model 08 — Collage & Papier

The user explicitly requested a new independent model for the supplied PNG homepage composition. Do not convert model 06A into model 08 and do not delete any earlier proposal. The stable model identifiers remain v1, v2, v3, v4, v5, v6a, v6b and v08.

## Composition

A large irregular, photocopy-treated restaurant photo on the left; `Wein. Tapas. Leben.` in the centre; a real wine bottle and torn-paper shop note on the right. Carry this paper, typography, photographic and dark torn-footer treatment through the complete restaurant, the shop homepage, product pages, cart and review checkout. Keep German as the main language. Do not use the rejected green star or the fabricated scene made from the owners' portraits.

## Shared functionality

The model uses the complete menu in `src/catalog.json`, the same product catalogue and existing review cart. News and the Instagram gallery use `shared/content.json` where available. The Instagram gallery is explicitly a preview, not an authorized live account connection. The event/catering inquiry form opens an email draft and never claims the email was sent automatically. Payments stay disabled. Management remains a separate shared entry.

## Rebuild

1. Preserve the current source restaurant and paired shop pages.
2. Run `python3 tools/product_photos.py` to install and apply the requested package photos to all shop designs.
3. Run `python3 tools/qa_product_photos.py` before adding 08 to the initial seven-model catalogue.
4. Run `python3 tools/build_model08.py` to update the existing 08 directory and refresh its selector card, not add another model.
5. Generate fresh thumbnails from the resulting pages before publishing.

If a generic build regenerates the seven-model selector, rerun step 4 and refresh the 08 thumbnails. Never describe a cached immutable review URL as automatically containing subsequent changes. Product images are sourced for this client review; image rights, final labels, stock and vintages must be cleared before a commercial launch.
