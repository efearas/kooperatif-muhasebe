function reCalculate()
	{
		runningTotal = 0;
		var KDVler = {};


		for(i=0; i<25; i++)
		{

			//abc
			//id_satisstokhareketleri_set-{{ forloop.counter0 }}-urun-birim_fiyat
			urun = $("#"+'id_satisstokhareketleri_set-'+ i +'-urun').val();
			//birimFiyat = $("#"+'id_satisstokhareketleri_set-'+ i +'-urun-birim_fiyat').val();
			birimFiyat = getFiyatByID(urun);
			$("#"+'id_satisstokhareketleri_set-'+ i +'-urun-birim_fiyat').val(birimFiyat);

			miktar = $("#"+'id_satisstokhareketleri_set-'+ i +'-miktar').val();
			//birim = $("#"+'birim_span_'+ i ).text();
			birim = getBirimByID(urun);

			tutar = 0;
			if(birim == 'Kg')
			{
				//tutar = Math.ceil(birimFiyat*miktar/1000);
				$("#"+'id_satisstokhareketleri_set-' + i + '-tutar').prop("readonly", false);
			}
			else
			{
				$("#"+'id_satisstokhareketleri_set-' + i + '-tutar').prop("readonly", true);
				tutar = birimFiyat*miktar;
			}

			tutar = tutar.toFixed(2);

			//if(!isNaN(tutar))
				//runningTotal = runningTotal+ parseFloat(tutar);


			//if(!isNaN(urun) && urun != "" && tutar != 0)
			if(!isNaN(urun) && urun != "" && birim != 'Kg')
			{
				$("#"+'id_satisstokhareketleri_set-' + i + '-tutar').val(tutar);

			}

			if(urun == "")
			{
				$("#"+'id_satisstokhareketleri_set-' + i + '-urun-birim_fiyat').val("");
				$("#"+'id_satisstokhareketleri_set-' + i + '-miktar').val("");
				$("#"+'id_satisstokhareketleri_set-' + i + '-tutar').val("");
			}


			//hesaplanan degil Tutar kutusuna elle yazilan rakam
			kutudakiTutar = $("#"+'id_satisstokhareketleri_set-' + i + '-tutar').val();
			if(kutudakiTutar != "" && kutudakiTutar != undefined)
			{
				kdvKategorisi = getKDVByID(urun);
				//kdvTutari = kutudakiTutar/100*kdvOrani;
				//kdvTutari = kdvTutari.toFixed(2);

				if(KDVler[kdvKategorisi] != undefined )
				{
					KDVler[kdvKategorisi] += parseFloat (kutudakiTutar);
				}
				else
				{
					KDVler[kdvKategorisi] = parseFloat (kutudakiTutar);
				}

				/*
				if(KDVler[kdvOrani] == undefined)
				{
					//KDVler[kdvOrani] = parseFloat( kdvTutari);
					KDVler[kdvOrani] += kutudakiTutar;
				}
				else
				{
					KDVler[kdvOrani] += kutudakiTutar;
					//KDVler[kdvOrani] = KDVler[kdvOrani] +  parseFloat( kdvTutari);
				}
				*/
				aaaa=7;
			}

		}

		TotalHesapla();
		KDVleriHesapla(KDVler);
		//$("#total").val(runningTotal);
	}

function KDVleriHesapla(KDVler)
	{
		$('#tablo-kdv tbody').empty();//rowlarin hepsini sil

		newRowContent="";
		for(var key in KDVler)
		{
			yeniKey = 'Kod yok, yanlış KDV oranı';

			if (key == 8)
			{
				yeniKey = 'K1';
			}
			if (key == 18)
			{
				yeniKey = 'K2';
			}

			if (key == 5)
			{
				yeniKey = 'K3';
			}

			if (key == 18)
			{
				yeniKey = 'K4';
			}


			newRowContent = "<tr><td>" + key +"</td><td></td><td>"+KDVler[key]+"</td><td></td></tr>";
			$("#tablo-kdv tbody").append(newRowContent);
		}

		//newRowContent = "<tr><td>" + "key" +"</td><td></td><td> KDVler[key] </td><td></td></tr>";


	}