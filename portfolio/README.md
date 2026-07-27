# Portfolio & Fiverr gig kit

Everything needed to list the three programs in [`programs/`](../programs/) as
Fiverr gigs: ready-to-paste gig copy, and portfolio images generated from the
programs' real output.

| Gig copy | Program | Images |
|---|---|---|
| [`gig-invoice-generator.md`](gig-invoice-generator.md) | [invoice-generator](../programs/invoice-generator/) | `invoice-document.png`, `invoice-system.png` |
| [`gig-web-scraper.md`](gig-web-scraper.md) | [web-scraper-to-csv](../programs/web-scraper-to-csv/) | `scraper-to-csv.png` |
| [`gig-bulk-image-processor.md`](gig-bulk-image-processor.md) | [bulk-image-processor](../programs/bulk-image-processor/) | `image-processor.jpg` |

Each gig file contains: title (plus alternates), category, search tags, a
three-tier package table with prices, package blurbs, the gig description,
FAQ, buyer requirements, and image captions. Descriptions are written to fit
Fiverr's 1,200-character limit and blurbs to the 100-character limit — the
counts in each file are exact.

## The images

| File | Size | Shows |
|---|---|---|
| `invoice-document.png` | 1411×1800 | A finished invoice as the client receives it |
| `invoice-system.png` | 1800×1563 | Terminal: batch run, payment recorded, receivables report + ledger |
| `scraper-to-csv.png` | 1800×1117 | Config on the left, the CSV it produced on the right |
| `image-processor.jpg` | 1800×1526 | Original → web → watermarked, with real file sizes |

**These are real output, not mockups.** Every number shown was produced by
running the programs: the invoice totals come from the generator, the CSV rows
from an actual scrape, the file sizes from an actual batch conversion. The
businesses and clients named (Northline Studio, Acme Interactive, Harbor Lane
Media, Vireo Labs, the demo shop) are invented for the samples, and the source
photos are this repo's own CC0 textures.

Fiverr's gig gallery wants at least 1280×769; these are larger, so they will
scale down cleanly. Crop to 1280×769 for the main gig image if you want tight
control over what shows in the thumbnail — the top-left of each sheet is
composed to survive that crop.

## Before you publish

- [ ] **Swap in your own business name.** The samples say "Northline Studio".
      Regenerate them with your details before posting — see below.
- [ ] **Decide what buyers actually receive.** The packages are written so
      Basic/Standard are done-for-you work and Premium hands over the tool.
      Make sure the delivery matches what you promise.
- [ ] **Set your prices.** The numbers in each gig file are a mid-market
      starting ladder, not researched rates. Check what's actually selling in
      each category and adjust before publishing.
- [ ] **Settle the code licence.** The repo's `LICENSE` covers *assets* as CC0
      and says nothing about `programs/`. If this repo is public, a buyer can
      find and download the code for free — which is fine if you're selling
      customisation and support, but decide deliberately. Options: keep it
      public as proof of work, add an explicit licence for `programs/`, or move
      the code to a private repo and keep the portfolio images here.
- [ ] **Only claim what you'll deliver.** Some listed features (email sending,
      Google Sheets output, scheduled runs, detail-page crawling) are gig extras
      that are *not built yet* — each program's README has them under "good next
      steps". Build them, or drop those lines from the gig.
- [ ] **Re-read the scraper gig's policy lines.** They're there to keep the gig
      approved and to set buyer expectations. Don't soften them to win an order.

## Regenerating the images with your own branding

The invoice images come straight from the program's example data:

```bash
cd programs/invoice-generator
# edit examples/config.json - your business name, address, tax ID, payment details
python3 invoice_generator.py new --config examples/config.json \
  --clients examples/clients.json --client acme --items examples/items.csv \
  --client-column client_id --out demo --date 2026-03-02 --po PO-8871
# open demo/INV-*.html in a browser and screenshot it, or print to PDF
```

For the watermark sheet, rerun the batch with your own studio name:

```bash
cd programs/bulk-image-processor
python3 imagebatch.py process ../../materials/Bricks097 --out proofs \
  --max 600 --watermark-text "© Your Studio" --manifest report.csv
```

The scraper sheet was built by running the scraper against a local demo shop, so
no live site was touched. Any public sandbox (`books.toscrape.com`,
`quotes.toscrape.com`) works the same way if you want to regenerate it.

## Answering buyers

Each program's README is the honest source of what it does today. When a buyer
asks whether something is possible, check the README's "For the next agent"
section — features listed there as next steps are not built yet. Quote the
build time accordingly rather than promising it as existing functionality.
