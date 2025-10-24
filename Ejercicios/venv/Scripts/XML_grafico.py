import xml.etree.ElementTree as ET
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import re

def parse_dian_xml(xml_content):
    """Parsea el XML DIAN y extrae la información de la factura"""
    
    # Limpiar el CDATA y obtener solo el contenido de Invoice
    cdata_match = re.search(r'<!\[CDATA\[(.*?)\]\]>', xml_content, re.DOTALL)
    if cdata_match:
        invoice_xml = cdata_match.group(1)
        root = ET.fromstring(invoice_xml)
    else:
        root = ET.fromstring(xml_content)
    
    namespaces = {
        '': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'sts': 'dian:gov:co:facturaelectronica:Structures-2-1'
    }
    
    # Extraer datos básicos
    factura = {
        'numero': root.find('.//cbc:ID', namespaces).text if root.find('.//cbc:ID', namespaces) is not None else 'N/A',
        'fecha_emision': root.find('.//cbc:IssueDate', namespaces).text if root.find('.//cbc:IssueDate', namespaces) is not None else 'N/A',
        'hora_emision': root.find('.//cbc:IssueTime', namespaces).text if root.find('.//cbc:IssueTime', namespaces) is not None else 'N/A',
        'cufe': root.find('.//cbc:UUID', namespaces).text if root.find('.//cbc:UUID', namespaces) is not None else 'N/A',
        'moneda': root.find('.//cbc:DocumentCurrencyCode', namespaces).text if root.find('.//cbc:DocumentCurrencyCode', namespaces) is not None else 'COP'
    }
    
    # Datos del emisor
    supplier = root.find('.//cac:AccountingSupplierParty', namespaces)
    if supplier is not None:
        factura['emisor'] = {
            'nombre': supplier.find('.//cbc:RegistrationName', namespaces).text if supplier.find('.//cbc:RegistrationName', namespaces) is not None else 'N/A',
            'nit': supplier.find('.//cbc:CompanyID', namespaces).text if supplier.find('.//cbc:CompanyID', namespaces) is not None else 'N/A',
            'direccion': supplier.find('.//cac:AddressLine/cbc:Line', namespaces).text if supplier.find('.//cac:AddressLine/cbc:Line', namespaces) is not None else 'N/A',
            'ciudad': supplier.find('.//cbc:CityName', namespaces).text if supplier.find('.//cbc:CityName', namespaces) is not None else 'N/A',
            'telefono': supplier.find('.//cbc:Telephone', namespaces).text if supplier.find('.//cbc:Telephone', namespaces) is not None else 'N/A',
            'email': supplier.find('.//cbc:ElectronicMail', namespaces).text if supplier.find('.//cbc:ElectronicMail', namespaces) is not None else 'N/A'
        }
    
    # Datos del receptor
    customer = root.find('.//cac:AccountingCustomerParty', namespaces)
    if customer is not None:
        factura['receptor'] = {
            'nombre': customer.find('.//cbc:RegistrationName', namespaces).text if customer.find('.//cbc:RegistrationName', namespaces) is not None else 'N/A',
            'nit': customer.find('.//cbc:CompanyID', namespaces).text if customer.find('.//cbc:CompanyID', namespaces) is not None else 'N/A',
            'direccion': customer.find('.//cac:AddressLine/cbc:Line', namespaces).text if customer.find('.//cac:AddressLine/cbc:Line', namespaces) is not None else 'N/A',
            'ciudad': customer.find('.//cbc:CityName', namespaces).text if customer.find('.//cbc:CityName', namespaces) is not None else 'N/A'
        }
    
    # Totales
    monetary = root.find('.//cac:LegalMonetaryTotal', namespaces)
    if monetary is not None:
        factura['totales'] = {
            'subtotal': monetary.find('.//cbc:LineExtensionAmount', namespaces).text if monetary.find('.//cbc:LineExtensionAmount', namespaces) is not None else '0',
            'iva': monetary.find('.//cbc:TaxInclusiveAmount', namespaces).text if monetary.find('.//cbc:TaxInclusiveAmount', namespaces) is not None else '0',
            'total': monetary.find('.//cbc:PayableAmount', namespaces).text if monetary.find('.//cbc:PayableAmount', namespaces) is not None else '0'
        }
    
    # Items de la factura
    factura['items'] = []
    for line in root.findall('.//cac:InvoiceLine', namespaces):
        item = {
            'id': line.find('.//cbc:ID', namespaces).text if line.find('.//cbc:ID', namespaces) is not None else 'N/A',
            'descripcion': line.find('.//cbc:Description', namespaces).text if line.find('.//cbc:Description', namespaces) is not None else 'N/A',
            'cantidad': line.find('.//cbc:InvoicedQuantity', namespaces).text if line.find('.//cbc:InvoicedQuantity', namespaces) is not None else '0',
            'precio': line.find('.//cbc:PriceAmount', namespaces).text if line.find('.//cbc:PriceAmount', namespaces) is not None else '0',
            'total': line.find('.//cbc:LineExtensionAmount', namespaces).text if line.find('.//cbc:LineExtensionAmount', namespaces) is not None else '0'
        }
        factura['items'].append(item)
    
    # Información de validación DIAN
    factura['dian'] = {
        'autorizacion': root.find('.//sts:InvoiceAuthorization', namespaces).text if root.find('.//sts:InvoiceAuthorization', namespaces) is not None else 'N/A',
        'qr_code': root.find('.//sts:QRCode', namespaces).text if root.find('.//sts:QRCode', namespaces) is not None else 'N/A'
    }
    
    return factura

def crear_pdf_factura(factura, filename):
    """Crea un PDF con la factura en formato formulario"""
    
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.darkblue,
        alignment=1,  # Centrado
        spaceAfter=30
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.darkblue,
        spaceAfter=12
    )
    
    # Contenido del PDF
    story = []
    
    # Título
    story.append(Paragraph("FACTURA ELECTRÓNICA DIAN", title_style))
    
    # Información básica
    info_basica = [
        [Paragraph("<b>Número Factura:</b>", styles['Normal']), factura['numero']],
        [Paragraph("<b>Fecha Emisión:</b>", styles['Normal']), f"{factura['fecha_emision']} {factura['hora_emision']}"],
        [Paragraph("<b>CUFE:</b>", styles['Normal']), factura['cufe'][:50] + "..."],  # Acortar CUFE para visualización
        [Paragraph("<b>Moneda:</b>", styles['Normal']), factura['moneda']]
    ]
    
    tabla_info = Table(info_basica, colWidths=[2*inch, 4*inch])
    tabla_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
    ]))
    
    story.append(tabla_info)
    story.append(Spacer(1, 20))
    
    # Información del emisor
    story.append(Paragraph("<b>EMISOR</b>", header_style))
    
    emisor_data = [
        [Paragraph("<b>Nombre:</b>", styles['Normal']), factura['emisor']['nombre']],
        [Paragraph("<b>NIT:</b>", styles['Normal']), factura['emisor']['nit']],
        [Paragraph("<b>Dirección:</b>", styles['Normal']), factura['emisor']['direccion']],
        [Paragraph("<b>Ciudad:</b>", styles['Normal']), factura['emisor']['ciudad']],
        [Paragraph("<b>Teléfono:</b>", styles['Normal']), factura['emisor']['telefono']],
        [Paragraph("<b>Email:</b>", styles['Normal']), factura['emisor']['email']]
    ]
    
    tabla_emisor = Table(emisor_data, colWidths=[1.5*inch, 4.5*inch])
    tabla_emisor.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
    ]))
    
    story.append(tabla_emisor)
    story.append(Spacer(1, 20))
    
    # Información del receptor
    story.append(Paragraph("<b>RECEPTOR</b>", header_style))
    
    receptor_data = [
        [Paragraph("<b>Nombre:</b>", styles['Normal']), factura['receptor']['nombre']],
        [Paragraph("<b>NIT:</b>", styles['Normal']), factura['receptor']['nit']],
        [Paragraph("<b>Dirección:</b>", styles['Normal']), factura['receptor']['direccion']],
        [Paragraph("<b>Ciudad:</b>", styles['Normal']), factura['receptor']['ciudad']]
    ]
    
    tabla_receptor = Table(receptor_data, colWidths=[1.5*inch, 4.5*inch])
    tabla_receptor.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgreen),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
    ]))
    
    story.append(tabla_receptor)
    story.append(Spacer(1, 20))
    
    # Tabla de items
    story.append(Paragraph("<b>DETALLE DE ITEMS</b>", header_style))
    
    # Encabezados de la tabla
    items_data = [['ID', 'Descripción', 'Cantidad', 'Precio Unit.', 'Total']]
    
    # Datos de los items
    for item in factura['items']:
        items_data.append([
            item['id'],
            Paragraph(item['descripcion'][:80] + "..." if len(item['descripcion']) > 80 else item['descripcion'], styles['Normal']),
            item['cantidad'],
            f"${float(item['precio']):,.2f}",
            f"${float(item['total']):,.2f}"
        ])
    
    tabla_items = Table(items_data, colWidths=[0.5*inch, 3*inch, 0.8*inch, 1*inch, 1*inch])
    tabla_items.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(tabla_items)
    story.append(Spacer(1, 20))
    
    # Totales
    story.append(Paragraph("<b>RESUMEN DE TOTALES</b>", header_style))
    
    totales_data = [
        [Paragraph("<b>Concepto</b>", styles['Normal']), Paragraph("<b>Valor</b>", styles['Normal'])],
        ['Subtotal', f"${float(factura['totales']['subtotal']):,.2f}"],
        ['IVA', f"${float(factura['totales']['iva']):,.2f}"],
        [Paragraph("<b>TOTAL A PAGAR</b>", styles['Normal']), Paragraph(f"<b>${float(factura['totales']['total']):,.2f}</b>", styles['Normal'])]
    ]
    
    tabla_totales = Table(totales_data, colWidths=[3*inch, 2*inch])
    tabla_totales.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 3), (-1, 3), colors.lightgrey),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(tabla_totales)
    story.append(Spacer(1, 20))
    
    # Información DIAN
    story.append(Paragraph("<b>INFORMACIÓN DIAN</b>", header_style))
    
    dian_data = [
        [Paragraph("<b>Autorización:</b>", styles['Normal']), factura['dian']['autorizacion']],
        [Paragraph("<b>QR Code:</b>", styles['Normal']), factura['dian']['qr_code']]
    ]
    
    tabla_dian = Table(dian_data, colWidths=[1.5*inch, 4.5*inch])
    tabla_dian.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightcoral),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
    ]))
    
    story.append(tabla_dian)
    
    # Generar PDF
    doc.build(story)
    print(f"PDF generado exitosamente: {filename}")

# Procesar tu XML
xml_content = """
<AttachedDocument xmlns="urn:oasis:names:specification:ubl:schema:xsd:AttachedDocument-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ccts="urn:un:unece:uncefact:data:specification:CoreComponentTypeSchemaModule:2" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:xades="http://uri.etsi.org/01903/v1.3.2#" xmlns:xades141="http://uri.etsi.org/01903/v1.4.1#">
<cbc:UBLVersionID>UBL 2.1</cbc:UBLVersionID>
<cbc:CustomizationID>Documentos adjuntos</cbc:CustomizationID>
<cbc:ProfileID>DIAN 2.1</cbc:ProfileID>
<cbc:ProfileExecutionID>WSHttpBinding_IWcfDianCustomerServices</cbc:ProfileExecutionID>
<cbc:ID>1SE2</cbc:ID>
<cbc:UUID schemeName="CUFE-SHA384">b2bfac3ae86aa34c9439d13befc5589a8cffe0ec7e88e7eec67edd734eb196610eea5143a802fd0f4c754e5d52a75d11</cbc:UUID>
<cbc:IssueDate>2022-06-14</cbc:IssueDate>
<cbc:IssueTime>10:36:05-05:00</cbc:IssueTime>
<cbc:DocumentType>Contenedor de Factura Electrónica</cbc:DocumentType>
<cbc:ParentDocumentID>1SE2</cbc:ParentDocumentID>
<cac:SenderParty>
<cac:PartyTaxScheme>
<cbc:RegistrationName>COMERCIALIZADORA LA ISABELA</cbc:RegistrationName>
<cbc:CompanyID schemeID="1" schemeAgencyID="195" schemeName="31">530520110</cbc:CompanyID>
<cbc:TaxLevelCode>O-13</cbc:TaxLevelCode>
<cac:TaxScheme>
<cbc:ID>ZZ</cbc:ID>
<cbc:Name>No aplica</cbc:Name>
</cac:TaxScheme>
</cac:PartyTaxScheme>
</cac:SenderParty>
<cac:ReceiverParty>
<cac:PartyTaxScheme>
<cbc:RegistrationName>EPS</cbc:RegistrationName>
<cbc:CompanyID schemeID="5" schemeAgencyID="195" schemeName="31">2222222244</cbc:CompanyID>
<cbc:TaxLevelCode>R-99-PN</cbc:TaxLevelCode>
<cac:TaxScheme>
<cbc:ID>ZZ</cbc:ID>
<cbc:Name>No aplica</cbc:Name>
</cac:TaxScheme>
</cac:PartyTaxScheme>
</cac:ReceiverParty>
<cac:Attachment>
<cac:ExternalReference>
<cbc:MimeCode>text/xml</cbc:MimeCode>
<cbc:EncodingCode>UTF-8</cbc:EncodingCode>
<cbc:Description>
<![CDATA[ <Invoice xmlns:sts="dian:gov:co:facturaelectronica:Structures-2-1" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xsi:schemaLocation="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2 http://docs.oasis-open.org/ubl/os-UBL-2.1/xsd/maindoc/UBL-Invoice-2.1.xsd" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:xades141="http://uri.etsi.org/01903/v1.4.1#" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:xades="http://uri.etsi.org/01903/v1.3.2#" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"> <ext:UBLExtensions> <ext:UBLExtension> <ext:ExtensionContent> <sts:DianExtensions> <sts:InvoiceControl> <sts:InvoiceAuthorization>18764028267127</sts:InvoiceAuthorization> <sts:AuthorizationPeriod> <cbc:StartDate>2020-01-01</cbc:StartDate> <cbc:EndDate>2080-12-31</cbc:EndDate> </sts:AuthorizationPeriod> <sts:AuthorizedInvoices> <sts:Prefix>1SE</sts:Prefix> <sts:From>1</sts:From> <sts:To>1000000</sts:To> </sts:AuthorizedInvoices> </sts:InvoiceControl> <sts:InvoiceSource> <cbc:IdentificationCode listAgencyID="6" listAgencyName="United Nations Economic Commission for Europe" listSchemeURI="urn:oasis:names:specification:ubl:codelist:gc:CountryIdentificationCode-2.1">CO</cbc:IdentificationCode> </sts:InvoiceSource> <sts:SoftwareProvider> <sts:ProviderID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)" schemeID="4" schemeName="31">530520110</sts:ProviderID> <sts:SoftwareID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)">75a7ccf4-1234-1aab-a6ee-40a0a0374547c</sts:SoftwareID> </sts:SoftwareProvider> <sts:SoftwareSecurityCode schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)">.....</sts:SoftwareSecurityCode> <sts:AuthorizationProvider> <sts:AuthorizationProviderID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)" schemeID="4" schemeName="31">800197268</sts:AuthorizationProviderID> </sts:AuthorizationProvider> <sts:QRCode>https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey=</sts:QRCode> </sts:DianExtensions> </ext:ExtensionContent> </ext:UBLExtension> <ext:UBLExtension> <ext:ExtensionContent> <CustomTagGeneral> <Interoperabilidad> <Group schemeName="Sector Salud"> <Collection schemeName="Usuario"> <AdditionalInformation> <Name>CODIGO_PRESTADOR</Name> <Value>1920304050</Value> </AdditionalInformation> <AdditionalInformation> <Name>MODALIDAD_PAGO</Name> <Value schemeName="salud_modalidad_pago.gc" schemeID="04">Pago por evento</Value> </AdditionalInformation> <AdditionalInformation> <Name>COBERTURA_PLAN_BENEFICIOS</Name> <Value schemeName="salud_cobertura.gc" schemeID="11">Plan medicina prepagada</Value> </AdditionalInformation> <AdditionalInformation> <Name>NUMERO_CONTRATO</Name> <Value>CNT-54200020-P1</Value> </AdditionalInformation> <AdditionalInformation> <Name>NUMERO_POLIZA</Name> <Value/> </AdditionalInformation> </Collection> </Group> </Interoperabilidad> </CustomTagGeneral> </ext:ExtensionContent> </ext:UBLExtension> <ext:UBLExtension> <ext:ExtensionContent> <ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#" Id="xmldsig-6d982761-6b02-4b76-b6fd-de10da178304"> <ds:SignedInfo> <ds:CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/> <ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha512"/> <ds:Reference Id="xmldsig-d1aa969a-3e6c-43ca-86e9-1ea43ec0526d-ref0" URI=""> <ds:Transforms> <ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/> </ds:Transforms> <ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha512"/> <ds:DigestValue>8aXCDZApxl6c/GFv4zMR0nXe2VW/fSDyfBeLn3GP4p6AtNGSfEvS8L2es1EspmS0VuJg6/Vvzd3lIWg2Aq70Iw==</ds:DigestValue> </ds:Reference> <ds:Reference Id="ReferenceKeyInfo" URI="#KeyInfoId-xmldsig-6d982761-6b02-4b76-b6fd-de10da178304"> <ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha512"/> <ds:DigestValue>E1KZALe4lu0vnXhDWMGOoKDlt6SV4eSCuDvaZniCfeagnHbuvNfA3UfQO2O4qOYL3ytkSQkox3LCiW79/sucmg==</ds:DigestValue> </ds:Reference> <ds:Reference Type="http://uri.etsi.org/01903#SignedProperties" URI="#SignedProperties-xmldsig-6d982761-6b02-4b76-b6fd-de10da178304"> <ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha512"/> <ds:DigestValue>8Rt/sHntDZO8tTmSzRA+uBrIJw2okBFwFcVaQNbVPjbuBiYhN3qNFWHQ3UvYlH5AtgR7YKUzYg9tYihWfQKpWA==</ds:DigestValue> </ds:Reference> </ds:SignedInfo> <ds:SignatureValue Id="xmldsig-6d982761-6b02-4b76-b6fd-de10da178304-sigvalue">DG4CXGenGc/9FKdHwpZPJIOGIRtz86drG4tSvwR25Tp8Sz8y5Cv5HSfpcPHstU0DOgGVMrB6P3L8L/J2qfLn621opNTvbNhYbjHWubTH1i144iExjmOJgiulySfPaWVLYBn3OJRSdmj19OY0ly9CopQUO5M0dSJjsNvck9n0psQL+WxfGlpmCU//TuKrhZNs2bZb/UWrkEkQcRlgRxl6KNbf5eG6TCFpGtmvkVDSsn3//uQwbbDfjrkLs5RZ37Dhf07LrOE98RG5vo5xouj10cREE42Gpw7kag7XfPH6e1VJqwSgZplixxVQvq0Wq1H79ctzat1LDJ1RLjz4ZQEktA==</ds:SignatureValue> <ds:KeyInfo Id="KeyInfoId-xmldsig-6d982761-6b02-4b76-b6fd-de10da178304"> <ds:X509Data> <ds:X509Certificate>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</ds:X509Certificate> </ds:X509Data> <ds:KeyValue> <ds:RSAKeyValue> <ds:Modulus>7xLWFOVQRaBgZXYihCz6NgjvXqnw9F0WIx0O0XlFYTFBmMjWl56Ih+xbZojttHyalOBWq/Ek7JsqnoXSs9X7FV/5d2PImMDE612AyRJlB4q2fv5VLp2HLzlzqDid4wJK+O/Ck5O/vD4oeYA6815h5g8OBd0Vb5fmi1QTXEVm6aEAUqQSDpNLHZm2SsKIiC0r2jJo13/Jk2yXpiqUmr72zO/Iy+RRO3+9QOZpYPu5asGm3jwAf1Fi8O7UthqcJmPeTpl6prnkRnYvKOLsVdiItK70EwD/K0PxqkhE3VQ7i4EI2FxgZuXyWR8MAUX8e3m+X1DZ0iRZuAfLLuMULxSsJw==</ds:Modulus> <ds:Exponent>AQAB</ds:Exponent> </ds:RSAKeyValue> </ds:KeyValue> </ds:KeyInfo> <ds:Object Id="XadesObjectId-19ac545d-000c-40d1-a6d8-39f11736dcf7"> <xades:QualifyingProperties xmlns:xades="http://uri.etsi.org/01903/v1.3.2#" Id="QualifyingProperties-4bd28828-ecae-42e6-9793-4fec0a2839fd" Target="#xmldsig-6d982761-6b02-4b76-b6fd-de10da178304"> <xades:SignedProperties Id="SignedProperties-xmldsig-6d982761-6b02-4b76-b6fd-de10da178304"> <xades:SignedSignatureProperties> <xades:SigningTime>2022-06-14T10:33:00-05:00</xades:SigningTime> <xades:SigningCertificate> <xades:Cert> <xades:CertDigest> <ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha512"/> <ds:DigestValue>AlWScIqircS/5hyKP92LjpS+Bo2rOuBTI6yghTOUGeynXi8LF2O41yy4JJV7KEZa9yEQGACIPyML9v/VZajI1A==</ds:DigestValue> </xades:CertDigest> <xades:IssuerSerial> <ds:X509IssuerName>C=CO, L=Bogota D.C., O=Andes SCD, OU=Division de certificacion entidad final, CN=CA ANDES SCD S.A. Clase II v2,1.2.840.113549.1.9.1=#1614696e666f40616e6465737363642e636f6d2e636f</ds:X509IssuerName> <ds:X509SerialNumber>5356046962897762017</ds:X509SerialNumber> </xades:IssuerSerial> </xades:Cert> </xades:SigningCertificate> <xades:SignaturePolicyIdentifier> <xades:SignaturePolicyId> <xades:SigPolicyId> <xades:Identifier>https://facturaelectronica.dian.gov.co/politicadefirma/v2/politicadefirmav2.pdf</xades:Identifier> <xades:Description>Política de firma para facturas electrónicas de la República de Colombia.</xades:Description> </xades:SigPolicyId> <xades:SigPolicyHash> <ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha512"/> <ds:DigestValue>Zcjw1Z9nGQn2j6NyGx8kAaLbOfJGd/fJxRTCeirlqAg7zRG27piJkJOpflGu7XACpMj9hC6dVMcCyzqHxxPZeQ==</ds:DigestValue> </xades:SigPolicyHash> <xades:SigPolicyQualifiers> <xades:SigPolicyQualifier> <xades:SPURI>https://facturaelectronica.dian.gov.co/politicadefirma/v2/politicadefirmav2.pdf</xades:SPURI> </xades:SigPolicyQualifier> </xades:SigPolicyQualifiers> </xades:SignaturePolicyId> </xades:SignaturePolicyIdentifier> <xades:SignerRole> <xades:ClaimedRoles> <xades:ClaimedRole>Rol Firmante</xades:ClaimedRole> </xades:ClaimedRoles> </xades:SignerRole> </xades:SignedSignatureProperties> <xades:SignedDataObjectProperties> <xades:DataObjectFormat ObjectReference="#xmldsig-d1aa969a-3e6c-43ca-86e9-1ea43ec0526d-ref0"> <xades:MimeType>text/xml</xades:MimeType> <xades:Encoding>UTF-8</xades:Encoding> </xades:DataObjectFormat> </xades:SignedDataObjectProperties> </xades:SignedProperties> </xades:QualifyingProperties> </ds:Object> </ds:Signature> </ext:ExtensionContent> </ext:UBLExtension> </ext:UBLExtensions> <cbc:UBLVersionID>UBL 2.1</cbc:UBLVersionID> <cbc:CustomizationID>SS-CUFE</cbc:CustomizationID> <cbc:ProfileID>DIAN 2.1: Factura Electrónica de Venta</cbc:ProfileID> <cbc:ProfileExecutionID>1</cbc:ProfileExecutionID> <cbc:ID>1SE2</cbc:ID> <cbc:UUID schemeID="1" schemeName="CUFE-SHA384">806d488ca9b7c2e843d22141290e32c88dda0cd7c1fdbb4429c85bb8174afff449aa2021e8f79405676e0be411066239</cbc:UUID> <cbc:IssueDate>2024-02-29</cbc:IssueDate> <cbc:IssueTime>10:41:27-05:00</cbc:IssueTime> <cbc:InvoiceTypeCode>01</cbc:InvoiceTypeCode> <cbc:TaxPointDate>2022-06-14</cbc:TaxPointDate> <cbc:DocumentCurrencyCode>COP</cbc:DocumentCurrencyCode> <cbc:LineCountNumeric>7</cbc:LineCountNumeric> <cac:InvoicePeriod> <cbc:StartDate>2024-06-01</cbc:StartDate> <cbc:EndDate>2024-06-30</cbc:EndDate> </cac:InvoicePeriod> <cac:AccountingSupplierParty> <cbc:AdditionalAccountID schemeAgencyID="195">1</cbc:AdditionalAccountID> <cac:Party> <cac:PartyName> <cbc:Name>HOSPITAL UNIVERSITARIO SAN IGNACIO</cbc:Name> </cac:PartyName> <cac:PhysicalLocation> <cac:Address> <cbc:ID>11001</cbc:ID> <cbc:CityName>Bogotá D.C.</cbc:CityName> <cbc:CountrySubentity>Bogotá D.C.</cbc:CountrySubentity> <cbc:CountrySubentityCode>11</cbc:CountrySubentityCode> <cac:AddressLine> <cbc:Line>Calle 41 No. 13-04 Piso 4</cbc:Line> </cac:AddressLine> <cac:Country> <cbc:IdentificationCode>CO</cbc:IdentificationCode> <cbc:Name languageID="es">Colombia</cbc:Name> </cac:Country> </cac:Address> </cac:PhysicalLocation> <cac:PartyTaxScheme> <cbc:RegistrationName>COMERCIALIZADORA LA ISABELA</cbc:RegistrationName> <cbc:CompanyID schemeID="1" schemeName="31" schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)">530520110</cbc:CompanyID> <cbc:TaxLevelCode>O-13</cbc:TaxLevelCode> <cac:RegistrationAddress> <cbc:ID>11001</cbc:ID> <cbc:CityName>Bogotá D.C.</cbc:CityName> <cbc:CountrySubentity>Bogotá D.C.</cbc:CountrySubentity> <cbc:CountrySubentityCode>11</cbc:CountrySubentityCode> <cac:AddressLine> <cbc:Line>Calle 41 No. 13-04 Piso 4</cbc:Line> </cac:AddressLine> <cac:Country> <cbc:IdentificationCode>CO</cbc:IdentificationCode> <cbc:Name languageID="es">Colombia</cbc:Name> </cac:Country> </cac:RegistrationAddress> <cac:TaxScheme> <cbc:ID>ZZ</cbc:ID> <cbc:Name>No aplica</cbc:Name> </cac:TaxScheme> </cac:PartyTaxScheme> <cac:PartyLegalEntity> <cbc:RegistrationName>COMERCIALIZADORA LA ISABELA</cbc:RegistrationName> <cbc:CompanyID schemeID="1" schemeName="31" schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)">530520110</cbc:CompanyID> <cac:CorporateRegistrationScheme> <cbc:ID>1SE</cbc:ID> </cac:CorporateRegistrationScheme> </cac:PartyLegalEntity> <cac:Contact> <cbc:Telephone>5946161</cbc:Telephone> <cbc:ElectronicMail>husifactura@husi.org.co</cbc:ElectronicMail> </cac:Contact> </cac:Party> </cac:AccountingSupplierParty> <cac:AccountingCustomerParty> <cbc:AdditionalAccountID schemeAgencyID="195">1</cbc:AdditionalAccountID> <cac:Party> <cac:PartyName> <cbc:Name>EPS</cbc:Name> </cac:PartyName> <cac:PhysicalLocation> <cac:Address> <cbc:ID>52001</cbc:ID> <cbc:CityName>Pasto</cbc:CityName> <cbc:CountrySubentity>Nariño</cbc:CountrySubentity> <cbc:CountrySubentityCode>52</cbc:CountrySubentityCode> <cac:AddressLine> <cbc:Line>CLL 17 27 25</cbc:Line> </cac:AddressLine> <cac:Country> <cbc:IdentificationCode>CO</cbc:IdentificationCode> <cbc:Name languageID="es">Colombia</cbc:Name> </cac:Country> </cac:Address> </cac:PhysicalLocation> <cac:PartyTaxScheme> <cbc:RegistrationName>EPS</cbc:RegistrationName> <cbc:CompanyID schemeID="5" schemeName="31" schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)">837000084</cbc:CompanyID> <cbc:TaxLevelCode>R-99-PN</cbc:TaxLevelCode> <cac:TaxScheme> <cbc:ID>ZZ</cbc:ID> <cbc:Name>No aplica</cbc:Name> </cac:TaxScheme> </cac:PartyTaxScheme> <cac:Contact> <cbc:Telephone>606123456789</cbc:Telephone> <cbc:ElectronicMail>facturacionelectronica@eps.com.co</cbc:ElectronicMail> </cac:Contact> </cac:Party> </cac:AccountingCustomerParty> <cac:PaymentMeans> <cbc:ID>1</cbc:ID> <cbc:PaymentMeansCode>10</cbc:PaymentMeansCode> </cac:PaymentMeans> <cac:PrepaidPayment> <cbc:ID schemeID="02">01</cbc:ID> <cbc:PaidAmount currencyID="COP">33004.00</cbc:PaidAmount> <cbc:ReceivedDate>2023-11-07</cbc:ReceivedDate> </cac:PrepaidPayment> <cac:TaxTotal> <cbc:TaxAmount currencyID="COP">0.0</cbc:TaxAmount> <cbc:RoundingAmount currencyID="COP">0.00</cbc:RoundingAmount> <cac:TaxSubtotal> <cbc:TaxableAmount currencyID="COP">333004.0</cbc:TaxableAmount> <cbc:TaxAmount currencyID="COP">0.0</cbc:TaxAmount> <cac:TaxCategory> <cbc:Percent>0.00</cbc:Percent> <cac:TaxScheme> <cbc:ID>01</cbc:ID> <cbc:Name>IVA</cbc:Name> </cac:TaxScheme> </cac:TaxCategory> </cac:TaxSubtotal> </cac:TaxTotal> <cac:LegalMonetaryTotal> <cbc:LineExtensionAmount currencyID="COP">333004.00</cbc:LineExtensionAmount> <cbc:TaxExclusiveAmount currencyID="COP">333004.00</cbc:TaxExclusiveAmount> <cbc:TaxInclusiveAmount currencyID="COP">333004.00</cbc:TaxInclusiveAmount> <cbc:AllowanceTotalAmount currencyID="COP">0.00</cbc:AllowanceTotalAmount> <cbc:ChargeTotalAmount currencyID="COP">0.00</cbc:ChargeTotalAmount> <cbc:PrepaidAmount currencyID="COP">33004.00</cbc:PrepaidAmount> <cbc:PayableRoundingAmount currencyID="COP">0.00</cbc:PayableRoundingAmount> <cbc:PayableAmount currencyID="COP">300000.00</cbc:PayableAmount> </cac:LegalMonetaryTotal> <cac:InvoiceLine> <cbc:ID>1</cbc:ID> <cbc:InvoicedQuantity unitCode="94">1.0</cbc:InvoicedQuantity> <cbc:LineExtensionAmount currencyID="COP">65700.0</cbc:LineExtensionAmount> <cac:TaxTotal> <cbc:TaxAmount currencyID="COP">0.0</cbc:TaxAmount> <cbc:RoundingAmount currencyID="COP">0.00</cbc:RoundingAmount> <cbc:TaxEvidenceIndicator>true</cbc:TaxEvidenceIndicator> <cac:TaxSubtotal> <cbc:TaxableAmount currencyID="COP">65700.0</cbc:TaxableAmount> <cbc:TaxAmount currencyID="COP">0.0</cbc:TaxAmount> <cac:TaxCategory> <cbc:Percent>0.00</cbc:Percent> <cac:TaxScheme> <cbc:ID>01</cbc:ID> <cbc:Name>IVA</cbc:Name> </cac:TaxScheme> </cac:TaxCategory> </cac:TaxSubtotal> </cac:TaxTotal> <cac:Item> <cbc:Description>CUPS:890702 - CONSULTA DE URGENCIAS</cbc:Description> <cbc:PackSizeNumeric>0</cbc:PackSizeNumeric> <cac:SellersItemIdentification> <cbc:ID>39145</cbc:ID> </cac:SellersItemIdentification> <cac:StandardItemIdentification> <cbc:ID schemeID="999" schemeName="EAN13">39145</cbc:ID> </cac:StandardItemIdentification> </cac:Item> <cac:Price> <cbc:PriceAmount currencyID="COP">65700.0</cbc:PriceAmount> <cbc:BaseQuantity unitCode="94">1.0</cbc:BaseQuantity> </cac:Price> </cac:InvoiceLine> <cac:InvoiceLine> <cbc:ID>2</cbc:ID> <cbc:InvoicedQuantity unitCode="94">1.0</cbc:InvoicedQuantity> <cbc:LineExtensionAmount currencyID="COP">62700.0</cbc:LineExtensionAmount> <cac:TaxTotal> <cbc:TaxAmount currencyID="COP">0.0</cbc:TaxAmount> <cbc:RoundingAmount currencyID="COP">0.00</cbc:RoundingAmount> <cbc:TaxEvidenceIndicator>true</cbc:TaxEvidenceIndicator> <cac:TaxSubtotal> <cbc:TaxableAmount currencyID="COP">62700.0</cbc:TaxableAmount> <cbc:TaxAmount currencyID="COP">0.0</cbc:TaxAmount> <cac:TaxCategory> <cbc:Percent>0.00</cbc:Percent> <cac:TaxScheme> <cbc:ID>01</cbc:ID> <cbc:Name>IVA</cbc:Name> </cac:TaxScheme> </cac:TaxCategory> </cac:TaxSubtotal> </cac:TaxTotal> <cac:Item> <cbc:Description>CUPS:971200 - INMOVILIZACIÓN MIEMBRO SUPERIOR O INFERIOR TOTAL O PARCIAL</cbc:Description> <cbc:PackSizeNumeric>0</cbc:PackSizeNumeric> <cac:SellersItemIdentification> <cbc:ID>37206</cbc:ID> </cac:SellersItemIdentification> <cac:StandardItemIdentification> <cbc:ID schemeID="999" schemeName="EAN13">37206</cbc:ID> </cac:StandardItemIdentification> </cac:Item> <cac:Price> <cbc:PriceAmount currencyID="COP">62700.0</cbc:PriceAmount> <cbc:BaseQuantity unitCode="94">1.0</cbc:BaseQuantity> </cac:Price> </cac:InvoiceLine> <cac:InvoiceLine> <cbc:ID>3</cbc:ID> <cbc:InvoicedQuantity unitCode="94">1.0</cbc:InvoicedQuantity> <cbc:LineExtensionAmount currencyID="COP">62700.0</cbc:LineExtensionAmount> <cac:TaxTotal> <cbc:TaxAmount currencyID="COP">0.0</cbc:TaxAmount> <cbc:RoundingAmount currencyID="COP">0.00</cbc:RoundingAmount> <cbc:TaxEvidenceIndicator>true</cbc:TaxEvidenceIndicator> <cac:TaxSubtotal> <cbc:TaxableAmount currencyID="COP">62700.0</cbc:TaxableAmount> <cbc:TaxAmount currencyID="COP">0.0</cbc:TaxAmount> <cac:TaxCategory> <cbc:Percent>0.00</cbc:Percent> <cac:TaxScheme> <cbc:ID>01</cbc:ID> <cbc:Name>IVA</cbc:Name> </cac:TaxScheme> </cac:TaxCategory> </cac:TaxSubtotal> </cac:TaxTotal> <cac:Item> <cbc:Description>CUPS:971200 - INMOVILIZACIÓN MIEMBRO SUPERIOR O INFERIOR TOTAL O PARCIAL</cbc:Description> <cbc:PackSizeNumeric>0</cbc:PackSizeNumeric> <cac:SellersItemIdentification> <cbc:ID>37206</cbc:ID> </cac:SellersItemIdentification> <cac:StandardItemIdentification> <cbc:ID schemeID="999" schemeName="EAN13">37206</cbc:ID> </cac:StandardItemIdentification> </cac:Item> <cac:Price> <cbc:PriceAmount currencyID="COP">62700.0</cbc:PriceAmount> <cbc:BaseQuantity unitCode="94">1.0</cbc:BaseQuantity> </cac:Price> </cac:InvoiceLine> <cac:InvoiceLine> <cbc:ID>4</cbc:ID> <cbc:InvoicedQuantity unitCode="94">1.0</cbc:InvoicedQuantity> <cbc:LineExtensionAmount currencyID="COP">56300.0</cbc:LineExtensionAmount> <cac:TaxTotal> <cbc:TaxAmount currencyID="COP">0.0</cbc:TaxAmount> <cbc:RoundingAmount currencyID="COP">0.00</cbc:RoundingAmount> <cbc:TaxEvidenceIndicator>true</cbc:TaxEvidenceIndicator> <cac:TaxSubtotal> <cbc:TaxableAmount currencyID="COP">56300.0</cbc:TaxableAmount> <cbc:TaxAmount currencyID="COP">0.0</cbc:TaxAmount> <cac:TaxCategory> <cbc:Percent>0.00</cbc:Percent> <cac:TaxScheme> <cbc:ID>01</cbc:ID> <cbc:Name>IVA</cbc:Name> </cac:TaxScheme> </cac:TaxCategory> </cac:TaxSubtotal> </cac:TaxTotal> <cac:Item> <cbc:Description>CUPS:873333 - MANO, DEDOS, PUÑO (MUÑECA), CODO, PIE, CLAVÍCULA, ANTEBRAZO, CUELLO DE PIE (TOBILLO), EDAD ÓSEA (CARPOGRAMA), CALCÁNEO</cbc:Description> <cbc:PackSizeNumeric>0</cbc:PackSizeNumeric> <cac:SellersItemIdentification> <cbc:ID>21101</cbc:ID> </cac:SellersItemIdentification> <cac:StandardItemIdentification> <cbc:ID schemeID="999" schemeName="EAN13">21101</cbc:ID> </cac:StandardItemIdentification> </cac:Item> <cac:Price> <cbc:PriceAmount currencyID="COP">56300.0</cbc:PriceAmount> <cbc:BaseQuantity unitCode="94">1.0</cbc:BaseQuantity> </cac:Price> </cac:InvoiceLine> <cac:InvoiceLine> <cbc:ID>5</cbc:ID> <cbc:InvoicedQuantity unitCode="94">1.0</cbc:InvoicedQuantity> <cbc:LineExtensionAmount currencyID="COP">56300.0</cbc:LineExtensionAmount> <cac:TaxTotal> <cbc:TaxAmount currencyID="COP">0.0</cbc:TaxAmount> <cbc:RoundingAmount currencyID="COP">0.00</cbc:RoundingAmount> <cbc:TaxEvidenceIndicator>true</cbc:TaxEvidenceIndicator> <cac:TaxSubtotal> <cbc:TaxableAmount currencyID="COP">56300.0</cbc:TaxableAmount> <cbc:TaxAmount currencyID="COP">0.0</cbc:TaxAmount> <cac:TaxCategory> <cbc:Percent>0.00</cbc:Percent> <cac:TaxScheme> <cbc:ID>01</cbc:ID> <cbc:Name>IVA</cbc:Name> </cac:TaxScheme> </cac:TaxCategory> </cac:TaxSubtotal> </cac:TaxTotal> <cac:Item> <cbc:Description>CUPS:873431 - MANO, DEDOS, PUÑO (MUÑECA), CODO, PIE, CLAVÍCULA, ANTEBRAZO, CUELLO DE PIE (TOBILLO), EDAD ÓSEA (CARPOGRAMA), CALCÁNEO</cbc:Description> <cbc:PackSizeNumeric>0</cbc:PackSizeNumeric> <cac:SellersItemIdentification> <cbc:ID>21101</cbc:ID> </cac:SellersItemIdentification> <cac:StandardItemIdentification> <cbc:ID schemeID="999" schemeName="EAN13">21101</cbc:ID> </cac:StandardItemIdentification> </cac:Item> <cac:Price> <cbc:PriceAmount currencyID="COP">56300.0</cbc:PriceAmount> <cbc:BaseQuantity unitCode="94">1.0</cbc:BaseQuantity> </cac:Price> </cac:InvoiceLine> <cac:InvoiceLine> <cbc:ID>6</cbc:ID> <cbc:InvoicedQuantity unitCode="94">4.0</cbc:InvoicedQuantity> <cbc:LineExtensionAmount currencyID="COP">11812.0</cbc:LineExtensionAmount> <cac:TaxTotal> <cbc:TaxAmount currencyID="COP">0.0</cbc:TaxAmount> <cbc:RoundingAmount currencyID="COP">0.00</cbc:RoundingAmount> <cbc:TaxEvidenceIndicator>true</cbc:TaxEvidenceIndicator> <cac:TaxSubtotal> <cbc:TaxableAmount currencyID="COP">11812.0</cbc:TaxableAmount> <cbc:TaxAmount currencyID="COP">0.0</cbc:TaxAmount> <cac:TaxCategory> <cbc:Percent>0.00</cbc:Percent> <cac:TaxScheme> <cbc:ID>01</cbc:ID> <cbc:Name>IVA</cbc:Name> </cac:TaxScheme> </cac:TaxCategory> </cac:TaxSubtotal> </cac:TaxTotal> <cac:Item> <cbc:Description>VENDA ALGODON NO ESTERIL 5X5</cbc:Description> <cbc:PackSizeNumeric>0</cbc:PackSizeNumeric> <cac:SellersItemIdentification> <cbc:ID>H100854</cbc:ID> </cac:SellersItemIdentification> <cac:StandardItemIdentification> <cbc:ID schemeID="999" schemeName="EAN13">H100854</cbc:ID> </cac:StandardItemIdentification> </cac:Item> <cac:Price> <cbc:PriceAmount currencyID="COP">2953.0</cbc:PriceAmount> <cbc:BaseQuantity unitCode="94">4.0</cbc:BaseQuantity> </cac:Price> </cac:InvoiceLine> <cac:InvoiceLine> <cbc:ID>7</cbc:ID> <cbc:Note>NON-STERILE ELASTIC BANDAGE 5X5</cbc:Note> <cbc:InvoicedQuantity unitCode="94">4.0</cbc:InvoicedQuantity> <cbc:LineExtensionAmount currencyID="COP">17492.0</cbc:LineExtensionAmount> <cac:TaxTotal> <cbc:TaxAmount currencyID="USD">0.0</cbc:TaxAmount> <cbc:RoundingAmount currencyID="USD">0.00</cbc:RoundingAmount> <cbc:TaxEvidenceIndicator>true</cbc:TaxEvidenceIndicator> <cac:TaxSubtotal> <cbc:TaxableAmount currencyID="USD">172.0</cbc:TaxableAmount> <cbc:TaxAmount currencyID="USD">0.0</cbc:TaxAmount> <cac:TaxCategory> <cbc:Percent>0.00</cbc:Percent> <cac:TaxScheme> <cbc:ID>01</cbc:ID> <cbc:Name>IVA</cbc:Name> </cac:TaxScheme> </cac:TaxCategory> </cac:TaxSubtotal> </cac:TaxTotal> <cac:Item> <cbc:Description>VENDA ELASTICA NO ESTERIL 5X5</cbc:Description> <cbc:PackSizeNumeric>0</cbc:PackSizeNumeric> <cac:SellersItemIdentification> <cbc:ID>H100905</cbc:ID> </cac:SellersItemIdentification> <cac:StandardItemIdentification> <cbc:ID schemeID="999" schemeName="EAN13">H100905</cbc:ID> </cac:StandardItemIdentification> </cac:Item> <cac:Price> <cbc:PriceAmount currencyID="COP">4373.0</cbc:PriceAmount> <cbc:BaseQuantity unitCode="94">4.0</cbc:BaseQuantity> </cac:Price> </cac:InvoiceLine> </Invoice> ]]>
</cbc:Description>
</cac:ExternalReference>
</cac:Attachment>
<cac:ParentDocumentLineReference>
<cbc:LineID>1</cbc:LineID>
<cac:DocumentReference>
<cbc:ID>1SE200000</cbc:ID>
<cbc:UUID schemeName="">806d488ca9b7c2e843d22141290e32c88dda0cd7c1fdbb4429c85bb8174afff449aa2021e8f79405676e0be411066239</cbc:UUID>
<cbc:IssueDate>2022-06-14</cbc:IssueDate>
<cbc:DocumentType>ApplicationResponse</cbc:DocumentType>
<cac:Attachment>
<cac:ExternalReference>
<cbc:MimeCode>text/xml</cbc:MimeCode>
<cbc:EncodingCode>UTF-8</cbc:EncodingCode>
<cbc:Description>
<![CDATA[ <?xml version="1.0" encoding="utf-8" standalone="no"?><ApplicationResponse xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:sts="dian:gov:co:facturaelectronica:Structures-2-1" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns="urn:oasis:names:specification:ubl:schema:xsd:ApplicationResponse-2"> <ext:UBLExtensions> <ext:UBLExtension> <ext:ExtensionContent> <sts:DianExtensions> <sts:InvoiceSource> <cbc:IdentificationCode listAgencyID="6" listAgencyName="United Nations Economic Commission for Europe" listSchemeURI="urn:oasis:names:specification:ubl:codelist:gc:CountryIdentificationCode-2.1">CO</cbc:IdentificationCode> </sts:InvoiceSource> <sts:SoftwareProvider> <sts:ProviderID schemeID="4" schemeName="31" schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)">800197268</sts:ProviderID> <sts:SoftwareID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)">...</sts:SoftwareID> </sts:SoftwareProvider> <sts:SoftwareSecurityCode schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)">...</sts:SoftwareSecurityCode> <sts:AuthorizationProvider> <sts:AuthorizationProviderID schemeID="4" schemeName="31" schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)">800197268</sts:AuthorizationProviderID> </sts:AuthorizationProvider> </sts:DianExtensions> </ext:ExtensionContent> </ext:UBLExtension> <ext:UBLExtension> <ext:ExtensionContent><ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#" Id="Signature-fb59b78d-4106-4970-9c76-bea41eed65bf"><ds:SignedInfo><ds:CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315" /><ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256" /><ds:Reference Id="Reference-1f819720-c8c5-436f-9895-322aa8080dbe" URI=""><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature" /></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256" /><ds:DigestValue>DNeQcomM0JccR9vrMsKd5dgH119w7qcieeYEyQmcAkc=</ds:DigestValue></ds:Reference><ds:Reference Id="ReferenceKeyInfo" URI="#Signature-fb59b78d-4106-4970-9c76-bea41eed65bf-KeyInfo"><ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256" /><ds:DigestValue>kjnvVxeVBJFQojy0gJISp5SIAaYib0cJ8ISAB/esluc=</ds:DigestValue></ds:Reference><ds:Reference Type="http://uri.etsi.org/01903#SignedProperties" URI="#xmldsig-Signature-fb59b78d-4106-4970-9c76-bea41eed65bf-signedprops"><ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256" /><ds:DigestValue>d0n/rqw+YmIFoXFOwO/oAJK0actb1XY7Dzl3BeV7odA=</ds:DigestValue></ds:Reference></ds:SignedInfo><ds:SignatureValue Id="SignatureValue-fb59b78d-4106-4970-9c76-bea41eed65bf">Yw/If7TwjCD/gOFB5Tw8do5juXFeK+z7lKCrPqCcyVtCuAM/VS78ZyHvtIirBlMsN00ZkPikhE6Uk0kRb7lQ4hlt9drp7mWfm4rgT8nWu4QivHECkUFNT3ZO/Wtxi9coG0giwj0oDCCwv6EPEGGGMHVJntNWk8EcLiowB3EqWkbV8wA9swx6rd1JIlAoS9pappSW4f6E814A785B6a2tI38wQDKqNezoHKETQ3sb7roFVs8cDxYtWRLcAvhCRH3LPfmA+TxqmgXCR2Y+C1cMetMjMLFS6GslfB3T6zTEev5ifkbn6lQkYezhko8WqpTUn4uXW3QL1qk7oqzkxzQ1TA==</ds:SignatureValue><ds:KeyInfo Id="Signature-fb59b78d-4106-4970-9c76-bea41eed65bf-KeyInfo"><ds:X509Data><ds:X509Certificate>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</ds:X509Certificate></ds:X509Data><ds:KeyValue><ds:RSAKeyValue><ds:Modulus>i/+fddBQbuWMCkXqYdPBJFTobo06mrTxvutKkNe0RJveG1SnKq15nvBft2h4nZF5EzPBKGKS3IWgsgmAd3yABhtvlOVoKxNFS3CWxO2oyyQ3ahuueWLA8tKeP/9M20/tWXT7T6FY5aaH4272BKiyYIzHnqPD43obZ5b1osLj0OPGbfkPi9gvVn6sinSeEZ0WXvDa1lrBB0q+wszmfT2lims0akoAzKgpU6yxQkRBQuPFPv9Wqgy6Ze1AtURpuX+Qyk4vZNonQjx7+IW2Z8v0htT9Yy8TpSK2r85wFYPs2V9IjCstZ49NXHKMoY5TLja9NZLPokIrlQV+aSiK8ojp0w==</ds:Modulus><ds:Exponent>AQAB</ds:Exponent></ds:RSAKeyValue></ds:KeyValue></ds:KeyInfo><ds:Object Id="XadesObjectId-f51ba3db-6c87-4821-beeb-94a51f8a3885"><xades:QualifyingProperties xmlns:xades="http://uri.etsi.org/01903/v1.3.2#" Id="QualifyingProperties-32fc9fe8-748d-41c4-ac0b-71afce5cc2e7" Target="#Signature-fb59b78d-4106-4970-9c76-bea41eed65bf"><xades:SignedProperties Id="xmldsig-Signature-fb59b78d-4106-4970-9c76-bea41eed65bf-signedprops"><xades:SignedSignatureProperties><xades:SigningTime>2022-06-14T10:40:56+00:00</xades:SigningTime><xades:SigningCertificate><xades:Cert><xades:CertDigest><ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256" /><ds:DigestValue>lOUQ66ufnUv0tTTWSw3IIIHw1AQvFSKUURutt0ZErm4=</ds:DigestValue></xades:CertDigest><xades:IssuerSerial><ds:X509IssuerName>C=CO, L=Bogota D.C., O=GSE, OU=PKI, CN=Autoridad Subordinada 01 GSE, E=info@gse.com.co</ds:X509IssuerName><ds:X509SerialNumber>199839390723768342225486</ds:X509SerialNumber></xades:IssuerSerial></xades:Cert></xades:SigningCertificate><xades:SignaturePolicyIdentifier><xades:SignaturePolicyId><xades:SigPolicyId><xades:Identifier>https://facturaelectronica.dian.gov.co/politicadefirma/v2/politicadefirmav2.pdf</xades:Identifier><xades:Description /></xades:SigPolicyId><xades:SigPolicyHash><ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256" /><ds:DigestValue>dMoMvtcG5aIzgYo0tIsSQeVJBDnUnfSOfBpxXrmor0Y=</ds:DigestValue></xades:SigPolicyHash></xades:SignaturePolicyId></xades:SignaturePolicyIdentifier><xades:SignerRole><xades:ClaimedRoles><xades:ClaimedRole>supplier</xades:ClaimedRole></xades:ClaimedRoles></xades:SignerRole></xades:SignedSignatureProperties><xades:SignedDataObjectProperties><xades:DataObjectFormat ObjectReference="#Reference-1f819720-c8c5-436f-9895-322aa8080dbe"><xades:MimeType>text/xml</xades:MimeType><xades:Encoding>UTF-8</xades:Encoding></xades:DataObjectFormat></xades:SignedDataObjectProperties></xades:SignedProperties></xades:QualifyingProperties></ds:Object></ds:Signature></ext:ExtensionContent> </ext:UBLExtension> </ext:UBLExtensions> <cbc:UBLVersionID>UBL 2.1</cbc:UBLVersionID> <cbc:CustomizationID>1</cbc:CustomizationID> <cbc:ProfileID>DIAN 2.1</cbc:ProfileID> <cbc:ProfileExecutionID>1</cbc:ProfileExecutionID> <cbc:ID>51840462</cbc:ID> <cbc:UUID schemeName="CUDE-SHA384">3acd3114b42cacbbd69bd5b0b5f410d85d94fcd8e507c3d66ba2609afc29fb61b8cd5588befb2c0d413fd8f23e5e92ac</cbc:UUID> <cbc:IssueDate>2022-06-14</cbc:IssueDate> <cbc:IssueTime>10:40:56-05:00</cbc:IssueTime> <cac:SenderParty> <cac:PartyTaxScheme> <cbc:RegistrationName>Unidad Especial Dirección de Impuestos y Aduanas Nacionales</cbc:RegistrationName> <cbc:CompanyID schemeID="4" schemeName="31">800197268</cbc:CompanyID> <cac:TaxScheme> <cbc:ID>01</cbc:ID> <cbc:Name>IVA</cbc:Name> </cac:TaxScheme> </cac:PartyTaxScheme> </cac:SenderParty> <cac:ReceiverParty> <cac:PartyTaxScheme> <cbc:RegistrationName>HOSPITAL UNIVERSITARIO SAN IGNACIO</cbc:RegistrationName> <cbc:CompanyID schemeID="1" schemeName="31">530520110</cbc:CompanyID> <cac:TaxScheme> <cbc:ID>01</cbc:ID> <cbc:Name>IVA</cbc:Name> </cac:TaxScheme> </cac:PartyTaxScheme> </cac:ReceiverParty> <cac:DocumentResponse> <cac:Response> <cbc:ResponseCode>02</cbc:ResponseCode> <cbc:Description>Documento validado por la DIAN</cbc:Description> </cac:Response> <cac:DocumentReference> <cbc:ID>1SE2</cbc:ID> <cbc:UUID schemeName="CUFE-SHA384">806d488ca9b7c2e843d22141290e32c88dda0cd7c1fdbb4429c85bb8174afff449aa2021e8f79405676e0be411066239</cbc:UUID> </cac:DocumentReference> <cac:LineResponse> <cac:LineReference> <cbc:LineID>1</cbc:LineID> </cac:LineReference> <cac:Response> <cbc:ResponseCode>0000</cbc:ResponseCode> <cbc:Description>0</cbc:Description> </cac:Response> </cac:LineResponse> <cac:LineResponse> <cac:LineReference> <cbc:LineID>2</cbc:LineID> </cac:LineReference> <cac:Response> <cbc:ResponseCode>0</cbc:ResponseCode> <cbc:Description>La Factura electrónica BTA-6975304, ha sido autorizada.</cbc:Description> </cac:Response> </cac:LineResponse> </cac:DocumentResponse> </ApplicationResponse> ]]>
</cbc:Description>
</cac:ExternalReference>
</cac:Attachment>
<cac:ResultOfVerification>
<cbc:ValidatorID>Unidad Especial Dirección de Impuestos y Aduanas Nacionales</cbc:ValidatorID>
<cbc:ValidationResultCode>02</cbc:ValidationResultCode>
<cbc:ValidationDate>2022-06-14</cbc:ValidationDate>
<cbc:ValidationTime>10:40:56-05:00</cbc:ValidationTime>
</cac:ResultOfVerification>
</cac:DocumentReference>
</cac:ParentDocumentLineReference>
</AttachedDocument>
"""

try:
    # Parsear el XML
    factura_data = parse_dian_xml(xml_content)
    
    # Crear nombre de archivo con fecha y número de factura
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"factura_{factura_data['numero']}_{fecha}.pdf"
    
    # Generar PDF
    crear_pdf_factura(factura_data, filename)
    
    print("Factura procesada exitosamente!")
    print(f"Número: {factura_data['numero']}")
    print(f"Emisor: {factura_data['emisor']['nombre']}")
    print(f"Receptor: {factura_data['receptor']['nombre']}")
    print(f"Total: ${float(factura_data['totales']['total']):,.2f}")
    
except Exception as e:
    print(f"Error al procesar el XML: {str(e)}")
