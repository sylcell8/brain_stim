VERSION=0.1.0
RELEASE=dev
PROJECTNAME=isee_engine
DOCDIR=doc
DOCTEMPLATEDIR=doc_template

doc: FORCE
	sphinx-apidoc -d 4 -H "iSee Engine" -A "Allen Institute for Brain Science" -V $(VERSION) -R $(VERSION).$(RELEASE) --full -o $(DOCDIR) $(PROJECTNAME)
	cp $(DOCTEMPLATEDIR)/*.rst $(DOCTEMPLATEDIR)/conf.py $(DOCDIR)
	sed -i --expression "s/|version|/${VERSION}/g" $(DOCDIR)/conf.py
	cp -R $(DOCTEMPLATEDIR)/_static $(DOCDIR)/_static
	cp -R $(DOCTEMPLATEDIR)/_templates $(DOCDIR)/_templates
	cd $(DOCDIR) && find . -name '*.rst' -exec sed -i --expression "s/|tgz_url|/${TGZ_URL}/g" {} \;
	cd $(DOCDIR) && find . -name '*.rst' -exec sed -i --expression "s/|zip_url|/${ZIP_URL}/g" {} \;	
	cd $(DOCDIR) && find . -name '*.rst' -exec sed -i --expression "s/|tgz_filename|/${TGZ_FILENAME}/g" {} \;
	cd $(DOCDIR) && find . -name '*.rst' -exec sed -i --expression "s/|zip_filename|/${ZIP_FILENAME}/g" {} \;
	cd $(DOCDIR) && make html || true

FORCE:

clean:
	rm -rf $(DOCDIR)